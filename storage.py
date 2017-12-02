import logging
import os
import sqlite3


class Storage:
    def __init__(self, name="main.db"):
        self.logger = logging.getLogger("db")
        if not os.path.exists(name):
            self.logger.warning("Database is not found.")
            self.logger.info("Trying to create database.")
            self.db = sqlite3.connect(name)
            try:
                creation = open("create.sql", "r")
                self.db.executescript("".join(creation.readlines()))
            except Exception as e:
                self.logger.critical("An error occurred during database creation: " + str(e))
                exit(-1)

            self.logger.info("Database has been created successfully and is ready for work.")
        else:
            self.logger.info("Trying to open database.")
            try:
                self.db = sqlite3.connect(name)
            except Exception as e:
                self.logger.critical("An error occurred during database opening: " + str(e))
                exit(-1)

            self.logger.info("DB has been opened successfully and is ready for work.")

    def add_user_if_needed(self, id, name, phone, token):
        self.logger.info("New user request.")
        resp = self.db.execute("SELECT id FROM Users WHERE name=? AND phone=? AND token=?",
                               (name, phone, token))

        success = False
        for i in resp:
            if i[0] == id:
                success = True

        if success:
            print("User {} already exists." % {id})
        else:
            print("User {} added." % {id})
            self.db.execute("INSERT INTO Users (id, name, phone, token) " +
                            "VALUES (?, ?, ?, ?)", (id, name, phone, token))

        self.db.commit()

    def get_user(self, id):
        self.logger.info("Get user request {}." % {id})
        resp = self.db.execute("SELECT id, name, phone, token FROM Users WHERE id=?", id)

        if (len(resp)) == 0:
            self.logger.warning("User {} not found." % {id})
        else:
            ret = []
            for i in resp:
                ret.append(list(i))
            return ret

    def delete_info(self, id, name, phone, token):
        self.logger.info("Delete user request {}." % {id})
        try:
            resp = self.db.execute("DELETE FROM Users WHERE id=? AND name=? AND phone=? AND token=?",
                                   (id, name, phone, token))
        except Exception as e:
            pass

        self.logger.info("User {} has been deleted." % {id})


