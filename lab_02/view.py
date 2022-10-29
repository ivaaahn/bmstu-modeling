from tkinter import *
from algs import calculate_probability, calculate_time


class UI:
    MAX_STATE_COUNT = 10
    MTRX: list[list[Entry]] = []
    RESULT: list[list[Entry]] = []

    def __init__(self) -> None:
        self._window: Tk = self._create_window()

        self._add_labels()
        self._add_state_buttons()

        self._add_matrix(1, 1)
        self._add_result(1, 14)

    def run(self) -> None:
        self._window.mainloop()

    def _create_window(self) -> Tk:
        window = Tk()
        window.title("Цепи Маркова")
        window.geometry("770x520")
        window.resizable(False, False)
        return window

    def _add_labels(self) -> None:
        Label(
            self._window,
            text="Кол-во состояний:",
            padx=20,
        ).grid(column=0, row=0)
        Label(self._window, text="Матрица: ", padx=20).grid(column=0, row=1)
        Label(self._window, text="Результат: ", padx=20).grid(column=0, row=14)

    def _add_state_buttons(self) -> None:
        for idx in range(1, self.MAX_STATE_COUNT + 1):
            cb = lambda n: lambda: self._update_state_count(n)
            Button(self._window, text=str("X"), command=cb(idx)).grid(
                column=idx + 1,
                row=0,
            )

        Button(
            self._window,
            text="Пуск",
            command=self._calculate,
        ).grid(column=1, row=13, columnspan=12, pady=20)

    def _add_matrix(self, start_column: int, start_row: int) -> None:
        for i in range(self.MAX_STATE_COUNT):
            row: list[Entry] = []
            for j in range(self.MAX_STATE_COUNT):
                Label(self._window, text=f"{i + 1}").grid(
                    column=start_column,
                    row=start_row + i + 1,
                )
                Label(self._window, text=f"{j + 1}:",).grid(
                    column=start_column + j + 1,
                    row=start_row,
                )

                cell = Entry(
                    self._window,
                    width=5,
                    fg="green",
                    font=("Arial", 16),
                )
                cell.grid(
                    column=start_column + j + 1,
                    row=start_row + i + 1,
                )
                cell.insert(END, "0")

                row.append(cell)

            self.MTRX.append(row)

    def _add_result(self, start_column: int, start_row: int) -> None:
        params = ("P", "t")

        for i, param in enumerate(params, start=1):
            row: list[Entry] = []
            for j in range(1, self.MAX_STATE_COUNT + 1):
                Label(master=self._window, text=param).grid(
                    column=start_column,
                    row=start_row + i,
                )
                Label(master=self._window, text="S" + str(j) + ":",).grid(
                    column=start_column + j,
                    row=start_row,
                )

                cell = Entry(
                    master=self._window,
                    width=5,
                    fg="green",
                    font=("Arial", 16),
                )
                cell.grid(column=start_column + j, row=start_row + i)

                cell.config(
                    state="readonly",
                    readonlybackground="red",
                )
                row.append(cell)

            self.RESULT.append(row)

    def _update_matrix(self, count: int) -> None:
        if count > self.MAX_STATE_COUNT:
            return

        for i in range(self.MAX_STATE_COUNT):
            for j in range(self.MAX_STATE_COUNT):
                if i > count - 1 or j > count - 1:
                    self.MTRX[i][j].delete(0, "end")
                    self.MTRX[i][j].config(state="disabled")
                else:
                    self.MTRX[i][j].config(state="normal")
                    self.MTRX[i][j].delete(0, "end")
                    self.MTRX[i][j].insert(END, "0")

    def _update_result(self, count: int) -> None:
        if count > self.MAX_STATE_COUNT:
            return

        for i in range(len(self.RESULT)):
            for j in range(self.MAX_STATE_COUNT):
                if j > count - 1:
                    self.RESULT[i][j].config(state="normal")
                    self.RESULT[i][j].delete(0, "end")
                    self.RESULT[i][j].config(state="disabled")
                else:
                    self.RESULT[i][j].config(state="normal")
                    self.RESULT[i][j].delete(0, "end")
                    self.RESULT[i][j].config(state="readonly")

    def _update_state_count(self, count: int) -> None:
        self._update_matrix(count)
        self._update_result(count)

    def _get_intensity_matrix(self) -> list[list[float]]:
        matrix: list[list[float]] = []
        for i in range(self.MAX_STATE_COUNT):
            row: list[float] = []

            for j in range(self.MAX_STATE_COUNT):
                if self.MTRX[i][j]["state"] == "normal":
                    row.append(float(self.MTRX[i][j].get()))

            if row:
                matrix.append(row)

        return matrix

    def _calculate(self) -> None:
        matrix = self._get_intensity_matrix()

        prob_res = calculate_probability(matrix)
        time_res = calculate_time(matrix, prob_res)

        result = [prob_res, time_res]

        for i in range(len(result)):
            for j in range(len(result[0])):
                self.RESULT[i][j].config(state="normal")
                self.RESULT[i][j].delete(0, "end")
                self.RESULT[i][j].insert(
                    END, "{:.2f}".format(round(result[i][j], 2))
                )
                self.RESULT[i][j].config(state="readonly")
