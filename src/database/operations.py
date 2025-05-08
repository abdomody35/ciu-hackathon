from psycopg2 import sql
from .connection import db


class DatabaseOperations:
    @staticmethod
    def create_record(table: str, data: dict):
        """Creates a new record in the specified table"""
        columns = list(data.keys())
        values = list(data.values())

        query = sql.SQL(
            "INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"
        ).format(
            table=sql.Identifier(table),
            columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in values),
        )

        return db.execute_query(query, values)

    @staticmethod
    def read_records(table: str, columns="*", conditions=None, limit=None):
        """Reads records from the specified table"""
        query = sql.SQL("SELECT {columns} FROM {table}").format(
            columns=sql.SQL(columns) if columns != "*" else sql.SQL("*"),
            table=sql.Identifier(table),
        )

        if conditions:
            query = query + sql.SQL(" WHERE {conditions}").format(
                conditions=sql.SQL(conditions)
            )

        if limit:
            query = query + sql.SQL(" LIMIT {limit}").format(limit=sql.Placeholder())
            return db.execute_query(query, [limit])

        return db.execute_query(query)

    @staticmethod
    def update_record(table: str, data: dict, conditions: str):
        """Updates records in the specified table"""
        set_items = [
            sql.SQL("{column} = {placeholder}").format(
                column=sql.Identifier(k), placeholder=sql.Placeholder(k)
            )
            for k in data.keys()
        ]

        query = sql.SQL(
            "UPDATE {table} SET {set_items} WHERE {conditions} RETURNING *"
        ).format(
            table=sql.Identifier(table),
            set_items=sql.SQL(", ").join(set_items),
            conditions=sql.SQL(conditions),
        )

        return db.execute_query(query, data)

    @staticmethod
    def delete_record(table: str, conditions: str):
        """Deletes records from the specified table"""
        query = sql.SQL("DELETE FROM {table} WHERE {conditions} RETURNING *").format(
            table=sql.Identifier(table), conditions=sql.SQL(conditions)
        )

        return db.execute_query(query)
