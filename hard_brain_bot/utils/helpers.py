import re


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
        "32": "Pinky Crush",
    }

    __PREVIOUS_STYLE = 32
    __valid_versions = frozenset(range(1, __PREVIOUS_STYLE + 1))

    @staticmethod
    def get_game_version_from_song_id(song_id: str) -> str:
        version_key = song_id[:2]
        if version_key in VersionHelper.versions.keys():
            return VersionHelper.versions[version_key]
        return "Unknown"

    @staticmethod
    def is_valid_version(version: int | str):
        return int(version) in VersionHelper.__valid_versions

    @staticmethod
    def get_game_versions(user_input: str) -> list[int]:
        CHAR_LIMIT = 80
        if len(user_input) > CHAR_LIMIT:
            raise ValueError(f"User input longer than {CHAR_LIMIT} characters")
        stripped = user_input
        for char in '-, ':
            stripped.replace(char, '')
        if not stripped.isnumeric():
            raise ValueError(
                "Invalid user input. Input should be comma-separated version numbers, with ranges separated by dashes (e.g. 1,2,3-5,7)"
            )
        return VersionHelper.__filter_versions(user_input)

    @staticmethod
    def __filter_versions(input_string: str) -> list[int]:
        result = set()

        for i in re.compile(r"(\d+)(?:-(\d+))?").finditer(input_string):
            start = int(i.group(1))
            end = int(i.group(2)) if i.group(2) else start
            result.update(range(start, end + 1))
        
        if not result.issubset(VersionHelper.__valid_versions):
            invalid_versions = result.difference(VersionHelper.__valid_versions)
            raise ValueError(f"Invalid user input. Version input contained invalid version(s) {''.join(invalid_versions)} (currently supporting 1-{VersionHelper.__PREVIOUS_STYLE - 1})")

        return sorted(result.intersection(VersionHelper.__valid_versions))
    
    @staticmethod
    def format_styles(styles: list[int]) -> str:
        formatted = [VersionHelper.versions[str(s).zfill(2)] for s in styles]
        return ', '.join(formatted)
