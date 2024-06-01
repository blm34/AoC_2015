from pathlib import Path
import json

import requests
import browser_cookie3 as bc3


class Communicator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._cookie = self.get_cookie()
        self._headers = {
            'User-Agent': ''  # ToDo: Include email and url to github repo where code can be seen here
        }
        self._root_folder = self.get_root_folder()

    def get_cookie(self):
        cookies = bc3.firefox(domain_name=".adventofcode.com")

        if ".adventofcode.com" not in str(cookies):
            input("Cookie not in Firefox. Temporarily Close chrome then press enter to continue")
            cookies = bc3.chrome(domain_name=".adventofcode.com")
            print("You may now reopen Chrome")

        if ".adventofcode.com" not in str(cookies):
            raise ValueError("Cannot find a cookie")

        return cookies

    def get_root_folder(self):
        path = Path().absolute()
        while path.name != "2015":
            path = path.parent
        return path

    def get_input(self, year: int, day: int):
        """
        Opens the given file. Typically a puzzle input

        Args:
            day: Load the puzzle input for this day.
            year: Load the puzzle input for this year.

        Returns:
            The contents of the file
        """
        filepath = Path.joinpath(self._root_folder, "input_files", f"{day}.txt")

        if not filepath.exists():
            puzzle_input = self.download_input(year, day)
            with open(filepath, 'w') as file:
                file.write(puzzle_input)

        with open(filepath, 'r') as file:
            puzzle_input = file.read().strip()

        return puzzle_input

    def download_input(self, year: int, day: int) -> str:
        """
        Download the puzzle input for the given day and year from the advent of code website, and return as a string.

        Args:
            day: Load the puzzle input for this day.
            year: Load the puzzle input for this year.

        Returns:
            The puzzle input for the given day
        """
        r = requests.get(f"https://adventofcode.com/{year}/day/{day}/input", headers=self._headers,
                         cookies=self._cookie)
        return r.text

    def check_answer(self, answer, year: int, day: int, level: int) -> bool:
        answers_filepath = Path.joinpath(self._root_folder, "answers", f"{year}.json")

        if not answers_filepath.is_file():
            self.create_answers_json(answers_filepath)

        with open(answers_filepath, 'r') as file:
            correct_answers = json.load(file)

        if correct_answers[str(day)][str(level)] is not None:
            return correct_answers[str(day)][str(level)] == answer

        elif self.upload_answer(answer, year, day, level):
            correct_answers[str(day)][str(level)] = answer
            with open(answers_filepath, 'w') as file:
                json.dump(correct_answers, file)
            return True
        else:
            return False

    def upload_answer(self, answer, year: int, day: int, level: int) -> bool:
        if input(f"Submit answer {answer} for level {level}").lower() != "y":
            print("Not submitting answer")
            return False

        url = f"https://adventofcode.com/{year}/day/{day}/answer"
        post_data = {'level': level, 'answer': str(answer)}
        response = requests.post(url, headers=self._headers, cookies=self._cookie, data=post_data)

        if response.status_code != 200:
            raise ValueError(f"Answer submission failed.\nStatus code: {response.status_code}\n\nResponse:\n{response.text}")

        print(f"Successfully submitted answer.\nResponse:\n{response.text}")

        if "That's the right answer!" in response.text:
            return True
        elif "That's not the right answer." in response.text:
            if "too low" in response.text:
                pass
            elif "too high" in response.text:
                pass
            return False
        elif "Did you already complete it" in response.text:
            raise ValueError("Problem already solved, answer should be stored")
        else:
            raise ValueError("Unexpected response message")

    def create_answers_json(self, path: Path):
        answers = {day: {1: None, 2: None} for day in range(1, 26)}
        with open(path, 'w') as file:
            json.dump(answers, file)


def communicator(year: int, day: int, level: int):
    def decorator(func):
        comm = Communicator()

        def new_func():
            input_data = comm.get_input(year, day)
            answer = func(input_data)
            check = comm.check_answer(answer, year, day, level)
            return answer, check
        return new_func
    return decorator