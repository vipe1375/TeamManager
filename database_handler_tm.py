import sqlite3
import os




class DatabaseHandler():
    def __init__(self, database_name : str):
        self.con = sqlite3.connect(f"{os.path.dirname(os.path.abspath(__file__))}/{database_name}")
        self.con.row_factory = sqlite3.Row

    # fonctions hors commandes

    def is_in_team(self, player_id, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"SELECT player_id FROM Players WHERE team_id = {team_id} AND player_id = {player_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        return result != []

    def get_team_id(self, guild_id):
        cursor = self.con.cursor()
        query = f"SELECT team_id FROM Teams WHERE guild_id = {guild_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        if result == [] or result == None:
            return None
        else:
            return result[0][0]

    def update_wr_p(self, player_id, team_id):
        cursor = self.con.cursor()
        query = f"SELECT wins, losses FROM Players WHERE player_id = {player_id} AND team_id = {team_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        wins, losses = result[0][0], result[0][1]
        wr = int(wins/(wins+losses)*100)

        query2 = f"UPDATE Players SET winrate = ? WHERE player_id = ? AND team_id = ?;"
        cursor.execute(query2, (wr, player_id, team_id))
        self.con.commit()
        cursor.close()

    def get_role(self, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"SELECT role_id FROM Teams WHERE team_id = {team_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        return result

    def update_wr_t(self, team_id: int):
        cursor = self.con.cursor()
        query = f"SELECT wins, losses FROM Teams WHERE team_id = {team_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        wins, losses = result[0][0], result[0][1]
        wr = int(wins/(wins+losses)*100)

        query2 = f"UPDATE Teams SET winrate = ? WHERE team_id = ?;"
        cursor.execute(query2, (wr, team_id))
        self.con.commit()
        cursor.close()

    

    # fonction des joueurs

    def add_win(self, player_id: int, nombre: int, guild_id: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"UPDATE Players SET wins = wins + ? WHERE player_id = ? AND team_id = ?;"
        cursor.execute(query, (nombre, player_id, team_id))
        self.con.commit()
        cursor.close()
        self.update_wr_p(player_id, team_id)

    def add_player(self, player_id: int, guild_id: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = "INSERT INTO Players(player_id, team_id) VALUES (?, ?);"
        cursor.execute(query, (player_id, team_id))
        self.con.commit()
        cursor.close()
        
    def add_mvp(self, player_id: int, guild_id: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"UPDATE Players SET mvp = mvp + 1 WHERE player_id = {player_id} AND team_id = {team_id};"
        cursor.execute(query)
        self.con.commit()
        cursor.close()

    def add_loss(self, player_id: int, nombre: int, guild_id: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"UPDATE Players SET losses = losses + {nombre} WHERE player_id = {player_id} AND team_id = {team_id};"
        cursor.execute(query)
        self.con.commit()
        cursor.close()
        self.update_wr_p(player_id, team_id)

    def get_lb(self, guild_id, theme: str) -> list:
        cursor = self.con.cursor()
        team_id = self.get_team_id(guild_id)
        if theme == "wr":
            query = f"SELECT player_id, winrate FROM Players WHERE team_id = {team_id} ORDER BY winrate DESC;"
        elif theme == "w":
            query = f"SELECT player_id, wins FROM Players WHERE team_id = {team_id} ORDER BY wins DESC;"
        elif theme == "l":
            query = f"SELECT player_id, losses FROM Players WHERE team_id = {team_id} ORDER BY losses DESC;"
        elif theme == "mvp":
            query = f"SELECT player_id, mvp FROM Players WHERE team_id = {team_id} ORDER BY mvp DESC;"

        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = list(map(list, result))
        return result

    def stats(self, player_id: int, guild_id: int) -> list:
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"SELECT wins, losses, winrate, mvp FROM Players WHERE team_id = {team_id} AND player_id = {player_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        return result




    # fonctions de gestion d'équipe


    def setup(self, guild_id: int, team_name: str, role_id: int) -> int:
        cursor = self.con.cursor()
        query = f"INSERT INTO Teams(guild_id, team_name, role_id) VALUES (?, ?, ?);"
        cursor.execute(query, (guild_id, team_name, role_id))
        self.con.commit()
        cursor.close()

    

    def players(self, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"SELECT player_id FROM Players WHERE team_id = {team_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        return result

    

    def team_win(self, guild_id: int, nombre: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = "UPDATE Teams SET wins = wins + ? WHERE team_id = ?"
        cursor.execute(query, (nombre, team_id))
        self.con.commit()
        cursor.close()
        self.update_wr_t(team_id)

    def team_loose(self, guild_id: int, nombre: int):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = "UPDATE Teams SET losses = losses + ? WHERE team_id = ?"
        cursor.execute(query, (nombre, team_id))
        self.con.commit()
        cursor.close()
        self.update_wr_t(team_id)

    def teamstats(self, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"SELECT team_name, wins, losses, winrate FROM Teams WHERE team_id = {team_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        result = list(map(list, result))
        return result

    """
    def roster_new(self, name, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"INSERT INTO Rosters(team_id, roster_name) VALUES (?, ?);"
        cursor.execute(query, (team_id, name))
        self.con.commit()
        cursor.close()

    def roster_add(self, player_id, guild_id):
        team_id = self.get_team_id(guild_id)
        cursor = self.con.cursor()
        query = f"INSERT INTO Players(team_id, roster_id) VALUES (?, ?);"
        cursor.execute(query, (team_id, name))
        self.con.commit()
        cursor.close()
    """