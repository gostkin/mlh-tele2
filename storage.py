import logging
import os
import sqlite3

import config


class Storage:
    def __init__(self, name=config.db):
        self.logger = logging.getLogger("root")
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

    def add_user_if_needed(self, id, phone, token):
        self.logger.info("New user request.")
        resp = self.db.execute("SELECT id FROM Users WHERE phone=? AND token=?",
                                   (phone, token))


        success = False
        if resp is not None:
            for i in resp:
                if i[0] == id:
                    success = True

        if success:
            print("User %d with such number already exists." % (id))
        else:
            print("User %d with number %s added." % (id, phone))
            self.db.execute("INSERT INTO Users (id, phone, token) " +
                            "VALUES (?, ?, ?)", (id,  phone, token))

        self.db.commit()

    def get_user_data(self, id):
        self.logger.info("Get user request %d." % (id))
        resp = self.db.execute("SELECT id, phone, token FROM Users WHERE id=?", [int(id)])

        resp = list(resp)
        if len(resp) == 0:
            self.logger.warning("User %d not found." % (id))
        else:
            ret = []
            for i in resp:
                ret.append(i)

            return ret

    def delete_info(self, id, phone):
        self.logger.info("Delete user request %d." % (id))
        try:
            resp = self.db.execute("DELETE FROM Users WHERE id=? AND phone=?",
                                   (int(id), phone))
            self.db.commit()
        except Exception as e:
            self.logger.warning(e)

        self.logger.info("User %d has been deleted." % (id))

    def close(self):
        self.db.close()

    def get_token(self, id, phone):
        self.logger.info("Get token user request %d." % (id))
        resp = self.db.execute("SELECT token FROM Users WHERE id=? AND phone=?", [int(id), phone])

        resp = list(resp)
        if len(resp) == 0:
            self.logger.warning("User %d not found." % (id))
            return None
        else:
            ret = []
            for i in resp:
                ret.append(i)

            return ret[0][0]

