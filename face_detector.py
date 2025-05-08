import cv2
import face_recognition
import numpy as np
import json
import os
import logging
import datetime

def apply_gamma_correction(image, gamma=1.0):
    """Apply gamma correction to the image."""
    # Build a lookup table mapping pixel values [0, 255] to adjusted gamma values
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
    # Apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def setup_logging(config):
    """Configure logging based on settings."""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    log_file = log_config.get("file", "face_detector.log")
    console_output = log_config.get("console", True)
    
    # Create logger
    logger = logging.getLogger("face_detector")
    logger.setLevel(log_level)
    logger.handlers = []  # Clear any existing handlers
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def load_config(config_file="config.json"):
    """Load configuration from JSON file."""
    default_config = {
        "input_image": "hall.jpg",
        "output_image": "detected_hall.jpg",
        "use_histogram_equalization": True,
        "use_gamma_correction": True,
        "gamma_value": 0.8,
        "face_detection_model": "hog",
        "save_intermediate_images": True,
        "logging": {
            "level": "INFO",
            "file": "face_detector.log",
            "console": True,
            "format": "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
        }
    }
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Set up basic logging to report config loading
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
            logging.info(f"Configuration loaded from '{config_file}'")
            return config
    except FileNotFoundError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        logging.warning(f"Config file '{config_file}' not found. Using default settings.")
        return default_config
    except json.JSONDecodeError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        logging.error(f"Invalid JSON in config file '{config_file}'. Using default settings.")
        return default_config

def main():
    # Load configuration
    config = load_config()
    
    # Set up logging with config settings
    logger = setup_logging(config)
    
    # Start execution timing
    start_time = datetime.datetime.now()
    logger.info(f"Face detection process started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract settings from config
    input_image = config["input_image"]
    output_image = config["output_image"]
    use_histogram_equalization = config["use_histogram_equalization"]
    use_gamma_correction = config["use_gamma_correction"]
    gamma_value = config["gamma_value"]
    face_detection_model = config["face_detection_model"]
    save_intermediate_images = config["save_intermediate_images"]
    
    # Log configuration
    logger.info(f"Configuration: {json.dumps({k: v for k, v in config.items() if k != 'logging'}, indent=2)}")
    
    # Check if input image exists
    if not os.path.exists(input_image):
        logger.error(f"Input image '{input_image}' not found.")
        return
    
    logger.info(f"Processing image: {input_image}")
    logger.info(f"Image enhancements: Histogram equalization={'Enabled' if use_histogram_equalization else 'Disabled'}, "
                f"Gamma correction={'Enabled (gamma={gamma_value})' if use_gamma_correction else 'Disabled'}")
    
    try:
        # 1. Load the image
        logger.debug("Loading image file")
        image = face_recognition.load_image_file(input_image)
        processed_image = image.copy()
        logger.debug(f"Image loaded: shape={image.shape}, dtype={image.dtype}")
        
        # 2. Apply histogram equalization if enabled
        if use_histogram_equalization:
            logger.debug("Applying histogram equalization")
            try:
                # Convert to grayscale for histogram equalization
                gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                # Apply histogram equalization
                equalized_gray = cv2.equalizeHist(gray_image)
                logger.debug("Histogram equalization completed")
                
                # Save intermediate result if requested
                if save_intermediate_images:
                    equalized_rgb = cv2.cvtColor(cv2.merge([equalized_gray, equalized_gray, equalized_gray]), cv2.COLOR_RGB2BGR)
                    equalized_output = f"equalized_{os.path.basename(input_image)}"
                    cv2.imwrite(equalized_output, equalized_rgb)
                    logger.info(f"Saved histogram equalized image to: {equalized_output}")
            except Exception as e:
                logger.error(f"Error during histogram equalization: {str(e)}")
        
        # 3. Apply gamma correction if enabled
        if use_gamma_correction:
            logger.debug(f"Applying gamma correction with gamma={gamma_value}")
            try:
                processed_image = apply_gamma_correction(processed_image, gamma=gamma_value)
                logger.debug("Gamma correction completed")
                
                # Save intermediate result if requested
                if save_intermediate_images:
                    gamma_output = f"gamma_{os.path.basename(input_image)}"
                    cv2.imwrite(gamma_output, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
                    logger.info(f"Saved gamma corrected image to: {gamma_output}")
            except Exception as e:
                logger.error(f"Error during gamma correction: {str(e)}")
        
        # 4. Detect face locations on the processed image
        logger.debug(f"Detecting faces using '{face_detection_model}' model")
        detection_start = datetime.datetime.now()
        face_locations = face_recognition.face_locations(processed_image, model=face_detection_model)
        detection_time = (datetime.datetime.now() - detection_start).total_seconds()
        logger.info(f"Found {len(face_locations)} faces in {detection_time:.2f} seconds")
        
        # 5. Convert to BGR for OpenCV drawing
        logger.debug("Converting image to BGR for visualization")
        output_image_bgr = cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
        
        # 6. Draw boxes around each face
        for i, (top, right, bottom, left) in enumerate(face_locations):
            width = right - left
            height = bottom - top
            cv2.rectangle(output_image_bgr, (left, top), (right, bottom), (0, 255, 0), 2)
            logger.debug(f"Face #{i+1}: position=({left},{top},{right},{bottom}), size={width}x{height} pixels")
        
        # 7. Save the result
        logger.debug(f"Saving output image to {output_image}")
        cv2.imwrite(output_image, output_image_bgr)
        logger.info(f"Saved output image with detected faces to: {output_image}")
        
        # Log execution time
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"Face detection process completed in {execution_time:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Unhandled exception during processing: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()