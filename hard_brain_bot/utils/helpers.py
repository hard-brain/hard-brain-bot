class VersionHelper:
    versions = {
        "01": "1st Style",
        "02": "2nd Style",
        "03": "3rd Style",
        "04": "4th Style",
        "05": "5th Style",
        "06": "6th Style",
        "07": "7th Style",
        "08": "8th Style",
        "09": "9th Style",
        "10": "10th Style",
        "11": "IIDX RED",
        "12": "HAPPY SKY",
        "13": "DistorteD",
        "14": "GOLD",
        "15": "DJ TROOPERS",
        "16": "EMPRESS",
        "17": "SIRIUS",
        "18": "Resort Anthem",
        "19": "Lincle",
        "20": "Tricoro",
        "21": "SPADA",
        "22": "PENDUAL",
        "23": "Copula",
        "24": "SINOBUZ",
        "25": "CANNON BALLERS",
        "26": "Rootage",
        "27": "HEROIC VERSE",
        "28": "BISTROVER",
        "29": "Cast Hour",
        "30": "RESIDENT",
        "31": "EPOLIS",
    }

    @staticmethod
    def get_game_version_from_song_id(song_id: str) -> str:
        version_key = song_id[:2]
        if version_key in VersionHelper.versions.keys():
            return VersionHelper.versions[version_key]
        return "Unknown"
