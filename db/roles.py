import sqlite3
from typing import List

import discord


class RolesDB:
    _db_file = "res/roles.db"

    def __init__(self):
        self.connection = sqlite3.connect(self._db_file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            print("closing the connection")
            self.connection.close()

    async def create_table(self, server: discord.Server):
        """ Creates a new table for the server if it doesn't exist"""
        q = '''CREATE TABLE IF NOT EXISTS `{0.id}`
        (role       INT     NOT NULL UNIQUE,
         alias      TEXT    NOT NULL,
         is_primary INT     NOT NULL DEFAULT 0)'''.format(server)
        self.connection.execute(q)
        self.connection.commit()

    async def sync(self, roles: List[discord.Role]):
        """ Syncs the roles with the server by adding any new entries"""
        if not roles:
            return

        server = roles[0].server
        self.create_table(server)
        for r in roles:
            self.insert(r)

    async def insert(self, role: discord.Role, alias=None, is_primary=0):
        """ Inserts a new role into the table.
            If the alias is not specified, the role name will be used instead
        """
        if not role:
            return

        server = role.server
        if alias is None:
            alias = role.name
        self.connection.execute(
            "INSERT OR IGNORE INTO `{0.id}` VALUES ('{1.id}', '{2}', '{3}')".format(server, role, alias, is_primary))
        self.connection.commit()

    async def update(self, role: discord.Role, alias=None):
        """ Updates the alias of a role
            If the alias is not specified, the role name will be used instead
        """
        server = role.server
        if alias is None:
            alias = role.name
        self.connection.execute(
            "UPDATE `{0.id}` SET alias = '{1}' WHERE role = '{2.id}'".format(server, alias, role))
        self.connection.commit()

    async def get(self, server, alias, is_primary=0):
        """ Gets the role info by its alias
        """
        cursor = self.connection.execute(
            "SELECT role FROM `{0.id}` WHERE alias = '{1}' AND is_primary = '{2}'".format(server, alias,
                is_primary))
        return cursor.fetchone()[0]

    async def getall(self, server):
        """ Gets all the roles
        """
        cursor = self.connection.execute("SELECT role FROM `{0.id}`".format(server))
        rows = cursor.fetchall()
        ret_list = []
        for r in rows:
            ret_list.append(str(r[0]))
        return ret_list

    async def getallmain(self, server):
        """ Gets the primary roles
        """
        cursor = self.connection.execute("SELECT role FROM `{0.id}` WHERE is_primary=1".format(server))
        rows = cursor.fetchall()
        ret_list = []
        for r in rows:
            ret_list.append(str(r[0]))
        return ret_list

    async def getallregular(self, server):
        """ Gets all the regular roles
        """
        cursor = self.connection.execute("SELECT role FROM `{0.id}`WHERE is_primary=0".format(server))
        rows = cursor.fetchall()
        ret_list = []
        for r in rows:
            ret_list.append(str(r[0]))
        return ret_list
