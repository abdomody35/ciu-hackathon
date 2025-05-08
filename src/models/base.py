from ..database.operations import DatabaseOperations


class BaseModel:
    table_name = None
    primary_key = ""
    fields = []

    @classmethod
    def create(self, **kwargs):
        """Creates a new record"""
        return DatabaseOperations.create_record(self.table_name, kwargs)

    @classmethod
    def getById(self, id):
        """Retrieves a single record by ID"""
        return DatabaseOperations.read_records(
            self.table_name, conditions=f"{self.primary_key} = {id}"
        )[0]

    @classmethod
    def getAll(self):
        """Retrieves all records"""
        return DatabaseOperations.read_records(self.table_name)

    @classmethod
    def update(self, id, **kwargs):
        """Updates an existing record"""
        return DatabaseOperations.update_record(
            self.table_name, kwargs, f"{self.primary_key} = {id}"
        )

    @classmethod
    def delete(self, id):
        """Deletes a record"""
        return DatabaseOperations.delete_record(
            self.table_name, f"{self.primary_key} = {id}"
        )
