__author__ = 'pfischi'

import sqlite3

from sonos_service import SonosSpeaker


class VwDeviceColumns():
        id = 'id'
        uid = 'uid'
        ip = 'ip'
        model = 'model'
        status = 'online'

class SonosDatabase():
    def __init__(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """ turning on foreign keys """
        self.conn.execute('PRAGMA foreign_keys=ON')

        """ Creating the necessary tables """

        stmt = 'CREATE TABLE IF NOT EXISTS tb_devices ' \
               '(id INTEGER PRIMARY KEY ASC, uid TEXT NOT NULL UNIQUE COLLATE NOCASE, model TEXT COLLATE NOCASE,' \
               'serial_number TEXT COLLATE NOCASE, software_version TEXT COLLATE NOCASE,' \
               'hardware_version TEXT COLLATE NOCASE, mac_address TEXT COLLATE NOCASE);'
        self.cursor.execute(stmt)

        stmt = 'CREATE TABLE IF NOT EXISTS tb_ip ' \
               '(id INTEGER PRIMARY KEY ASC, device_id INTEGER UNIQUE, ip INTEGER UNIQUE, ' \
               'FOREIGN KEY(device_id) REFERENCES tb_devices(id));'
        self.cursor.execute(stmt)

        stmt = 'CREATE TABLE IF NOT EXISTS tb_status ' \
               '(device_id INTEGER NOT NULL UNIQUE, online INTEGER DEFAULT 0 NOT NULL, ' \
               'last_refresh TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, ' \
               'FOREIGN KEY(device_id) REFERENCES tb_devices(id));'
        self.cursor.execute(stmt)

        stmt = 'CREATE TABLE IF NOT EXISTS tb_zones (id INTEGER PRIMARY KEY ASC, ' \
               'zone_name TEXT NOT NULL UNIQUE, zone_icon TEXT);'
        self.cursor.execute(stmt)

        " to examine: The device can belong to only one zone --> assuming yes "

        stmt = 'CREATE TABLE IF NOT EXISTS tb_zones_devices (device_id INTEGER UNIQUE NOT NULL, ' \
               'zone_id INTEGER NOT NULL, ' \
               'FOREIGN KEY(device_id) REFERENCES tb_devices(id), ' \
               'FOREIGN KEY(zone_id) REFERENCES tb_zones(id))'
        self.cursor.execute(stmt)

        stmt = 'CREATE VIEW IF NOT EXISTS vw_devices AS SELECT t1.id, t1.uid, t2.ip, t1.model, t3.online, t5.zone_name,' \
               't5.zone_icon, t1.software_version, t1.hardware_version, t1.mac_address, t1.serial_number ' \
               'FROM tb_devices as t1 ' \
               'JOIN tb_ip as t2 ON t2.device_id = t1.id ' \
               'JOIN tb_status as t3 ON t3.device_id = t1.id '\
               'LEFT JOIN tb_zones_devices as t4 ON t1.id = t4.device_id '\
               'LEFT JOIN tb_zones as t5 ON t5.id = t4.zone_id;'
        self.cursor.execute(stmt)

        self.conn.commit()

    def add_speaker(self, speaker):

        try:
            stmt = 'INSERT OR IGNORE INTO tb_devices (uid) VALUES (?);'
            self.cursor.execute(stmt, (speaker.uid,))
            self.conn.commit()

            stmt = 'SELECT id FROM tb_devices WHERE uid = ?;'
            self.cursor.execute(stmt, [speaker.uid, ])

            last_inserted_id, = self.cursor.fetchone()

            'adding model separately, because INSERT OR IGNORE statement can cause an empty model column '
            data = [speaker.model, last_inserted_id]
            stmt = 'UPDATE tb_devices SET model = ? WHERE id = ?'
            self.cursor.execute(stmt, data)

            data = [last_inserted_id, speaker.ip]
            stmt = 'INSERT OR REPLACE INTO tb_ip (device_id, ip) VALUES (?,?);'
            self.cursor.execute(stmt, data)

            data = [last_inserted_id, 1]
            stmt = 'INSERT OR REPLACE INTO tb_status (device_id, online) VALUES (?,?)'
            self.cursor.execute(stmt, data)

            self.conn.commit()

            return last_inserted_id

        except Exception as err:
            self.conn.rollback()
            raise Exception('Unable to add sonos speaker with uid \'{}\'!\n{}'.format(speaker.uid, err))

    def set_speaker_info(self, speaker):

        try:
            data = [speaker.serial_number, speaker.software_version, speaker.hardware_version, speaker.mac_address,
                    speaker.model, speaker.uid]

            stmt = 'UPDATE tb_devices SET serial_number = ?, software_version = ?, hardware_version = ?, ' \
                   'mac_address = ?, model = ? ' \
                   'WHERE uid = ?;'
            self.cursor.execute(stmt, data)

            stmt = 'INSERT OR IGNORE INTO tb_zones (zone_name, zone_icon) VALUES(?,?);'
            self.cursor.execute(stmt, [speaker.zone_name, speaker.zone_icon])

            stmt = 'SELECT id FROM tb_zones WHERE zone_name = ?;'
            self.cursor.execute(stmt, [speaker.zone_name, ])

            last_insert_zone_id, = self.cursor.fetchone()

            stmt = 'INSERT OR REPLACE INTO tb_zones_devices (device_id, zone_id) VALUES(?,?);'
            self.cursor.execute(stmt, [speaker.id, last_insert_zone_id])

            self.conn.commit()

        except Exception as err:
            self.conn.rollback()
            raise Exception('Unable to set detailed information of sonos speaker with uid \'{}\'!\n{}'.format(speaker.uid, err))

    def set_speakers_offline(self):
        """ set all devices to offline status """
        stmt = 'UPDATE tb_status SET online = 0, last_refresh = datetime();'
        self.cursor.execute(stmt)
        self.conn.commit()

    def speakers_list(self, query_options=None):
        """list all devices in network """

        query =''

        loop = 0
        for k, v in query_options.items():
            if loop is 0:
                query += 'WHERE {} = ? AND '.format(k)
                loop += 1
            else:
                query += '{} = ? AND '.format(k)
        query = query.rstrip('AND ') + ';'

        stmt = 'SELECT * FROM vw_devices {}'.format(query)

        self.cursor.execute(stmt, list(query_options.values()))

        rows = self.cursor.fetchall()

        speakers = []

        for row in rows:
            speaker = SonosSpeaker()
            speaker.id = row[0]
            speaker.uid = row[1]
            speaker.ip = row[2]
            speaker.model = row[3]
            speaker.status = row[4]
            speaker.zone_name = row[5]
            speaker.zone_icon = row[6]
            speaker.software_version = row[7]
            speaker.hardware_version = row[8]
            speaker.mac_address = row[9]
            speaker.serial_number = row[10]
            speakers.append(speaker)

        return speakers
