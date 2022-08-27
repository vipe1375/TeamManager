import sqlite3
import os

# Teams: guild_id | team_name | wins | losses | winrate | role_id

# Players: player_id | team_id | wins | losses | winrate | mvp


class DatabaseHandler():
    def __init__(self, database_name : str):
        self.con = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}/{database_name}")
        self.con.row_factory = sqlite3.Row

    def get_player_info(self, player_id, guild_id):
        cursor = self.con.cursor()
        query = f"SELECT * FROM Players WHERE team_id = {guild_id} AND player_id = {player_id};"
        cursor.execute(query)
        result = cursor.fetchone()
        return result

    def get_team_info(self, guild_id):
        cursor = self.con.cursor()
        query = f"SELECT * FROM Teams WHERE guild_id = {guild_id};"
        cursor.execute(query)
        result = cursor.fetchone()
        return result

    def is_in_team(self, player_id, guild_id):
        cursor = self.con.cursor()
        query = f"SELECT player_id FROM Players WHERE team_id = {guild_id} AND player_id = {player_id};"
        cursor.execute(query)
        result = cursor.fetchone()
        return result != None

    def update_wr_p(self, player_id, guild_id):
        cursor = self.con.cursor()
        result = self.get_player_info(player_id, guild_id)
        wins, losses = result[2], result[3]
        wr = int(wins/(wins+losses)*100)

        query2 = f"UPDATE Players SET winrate = ? WHERE player_id = ? AND team_id = ?;"
        cursor.execute(query2, (wr, player_id, guild_id))
        self.con.commit()
        cursor.close()

    def update_wr_t(self, guild_id):
        cursor = self.con.cursor()
        result = self.get_team_info(guild_id)
        wins, losses = result[3], result[4]
        wr = int(wins/(wins+losses)*100)

        query2 = f"UPDATE Teams SET winrate = ? WHERE guild_id = ?;"
        cursor.execute(query2, (wr, guild_id))
        self.con.commit()
        cursor.close()

    def add_player_stat(self, player_id, guild_id, wins:int=0, losses:int=0, mvp:int=0):
        cursor = self.con.cursor()
        query = f"UPDATE Players SET wins = wins + {wins}, losses = losses + {losses}, mvp = mvp + {mvp} WHERE player_id = {player_id} AND team_id = {guild_id};"
        cursor.execute(query)
        self.con.commit()
        cursor.close()
        self.update_wr_p(player_id, guild_id)

    def add_team_stat(self, guild_id, wins: int = 0, losses: int = 0):
        cursor = self.con.cursor()
        query = f"UPDATE Teams SET wins = wins + {wins}, losses = losses + {losses} WHERE guild_id = {guild_id};"
        cursor.execute(query)
        self.con.commit()
        cursor.close()
        self.update_wr_t(guild_id)

    def add_player(self, player_id:int, guild_id:int):
        cursor = self.con.cursor()
        query = "INSERT INTO Players(player_id, team_id) VALUES (?, ?);"
        cursor.execute(query, (player_id, guild_id))
        self.con.commit()
        cursor.close()

    def remove_player(self, player_id, guild_id):
        cursor = self.con.cursor()
        query = f"DELETE From Players WHERE player_id = ? AND team_id = ?;"
        cursor.execute(query, (player_id, guild_id))
        self.con.commit()
        cursor.close()

    def get_lb(self, guild_id, theme: str):
        
        cursor = self.con.cursor()
        team_id = guild_id
        if theme == "wr":
            query = f"SELECT player_id, winrate FROM Players WHERE team_id = {team_id} ORDER BY winrate DESC;"
        elif theme == "w":
            query = f"SELECT player_id, wins FROM Players WHERE team_id = {team_id} ORDER BY wins DESC;"
        elif theme == "l":
            query = f"SELECT player_id, losses FROM Players WHERE team_id = {team_id} ORDER BY losses DESC;"
        elif theme == "mvp":
            query = f"SELECT player_id, mvp FROM Players WHERE team_id = {team_id} ORDER BY mvp DESC;"

        cursor.execute(query)
        result = cursor.fetchmany(10)
        cursor.close()
        return result

    def setup(self, guild_id: int, team_name: str, role_id: int, nb_w, nb_l) -> int:
        cursor = self.con.cursor()
        query = f"INSERT INTO Teams(guild_id, team_name, role_id, wins, losses) VALUES (?, ?, ?, ?, ?);"
        cursor.execute(query, (guild_id, team_name, role_id, nb_w, nb_l))
        self.con.commit()
        cursor.close()

    def players(self, guild_id):
        cursor = self.con.cursor()
        query = f"SELECT player_id FROM Players WHERE team_id = {guild_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        return result