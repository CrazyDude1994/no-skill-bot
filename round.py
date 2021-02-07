from asyncio import create_task, sleep
from random import shuffle
from urllib.parse import unquote


class Round:
    def __init__(self, channel, questions, rounds, source) -> None:
        super().__init__()
        self.answers = {}
        self.rounds = rounds
        self.current_question = 0
        self.questions = questions
        self.channel = channel
        self.points = {}
        self.no_answers_count = 0
        self.task = create_task(self.start_game())
        self.source = source

    def add_answer(self, author, answer):
        if author not in self.answers:
            self.answers[author] = answer

    async def start_game(self):
        await self.channel.send("`Starting new game of trivia`")
        while self.current_question < len(self.questions):
            if self.no_answers_count == 3:
                await self.channel.send("> There were no answers in the past 3 rounds. Stopping current game")
                self.task.cancel()
                self.rounds.remove(self)
                return
            await self.start_round()
        leaderboard = dict(reversed(sorted(self.points.items(), key=lambda item: item[1])))
        results_message = ["> **Game results**"]
        for index, (user, points) in enumerate(leaderboard.items()):
            results_message.append("> {0}) **{1}** - {2} points".format(index + 1, user.name, points))
        await self.channel.send("\r\n".join(results_message))
        self.source.remove(self)

    async def start_round(self):
        self.answers.clear()
        question = self.questions[self.current_question]
        variants = [question["correct_answer"]]
        variants.extend(question["incorrect_answers"])
        variants = [unquote(i) for i in variants]
        answer = variants[0]
        shuffle(variants)
        answer_number = variants.index(answer) + 1
        await self.channel.send("""
        > :mega: Question {0} of {1}
        > 
        > **{2}**
        > *You have {3} seconds to answer*
        > :one:  {4}
        > :two:  {5}
        > :three:  {6}
        > :four:  {7}
        > 
        > :notepad_spiral: *{8}*
        > :lock: *{9}*
        """.format(self.current_question + 1, len(self.questions), unquote(question["question"]), 15, variants[0],
                   variants[1], variants[2], variants[3], unquote(question["category"]),
                   question["difficulty"].capitalize()))
        await sleep(15)
        correct_users = []
        for user, user_answer in self.answers.items():
            if user_answer.isnumeric() and int(user_answer) == answer_number:
                if user in self.points:
                    self.points[user] += 1
                else:
                    self.points[user] = 1
                correct_users.append(user)
        self.current_question += 1
        await self.channel.send("> Correct answer was **{0}**".format(answer));
        if len(correct_users) > 0:
            await self.channel.send("> {0} were right".format(", ".join([str(user.name) for user in correct_users])))
        await sleep(3)
        if len(self.answers) == 0:
            self.no_answers_count += 1
        else:
            self.no_answers_count = 0
