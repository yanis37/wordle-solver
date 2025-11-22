import tkinter as tk
from tkinter import messagebox
import random
from collections import Counter

WORDLIST_FILE = "./valid-wordle-words.txt"
starters = ["crane", "slate", "audio", "soare", "roate", "arise", "ratio", "adieu", "stare", "trace"]


class WordleAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wordle Assistant")
        self.configure(bg="#121213")
        self.resizable(False, False)
        self.all_words = self.load_words()
        if not self.all_words:
            messagebox.showerror("Erreur", f"Impossible de charger {WORDLIST_FILE}")
            self.destroy()
            return
        self.starters = [w for w in starters if w in self.all_words]
        if not self.starters:
            self.starters = list(self.all_words)
        self.max_rows = 6
        self.cols = 5
        self.cells = []
        self.feedback_states = []
        self.current_row = 0
        self.current_guess = None
        self.remaining_words = list(self.all_words)
        self.guesses = []
        self.green_letters = set()
        self.yellow_letters = set()
        self.gray_letters = set()
        self.game_over = False
        self.top_list = []
        self.letters_var = tk.StringVar()
        self.build_ui()
        self.start_new_game()

    def load_words(self):
        try:
            with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
                return [w.strip().lower() for w in f if len(w.strip()) == 5 and w.strip().isalpha()]
        except Exception:
            return []

    def build_ui(self):
        main_frame = tk.Frame(self, bg="#121213")
        main_frame.pack(padx=15, pady=15)
        grid_frame = tk.Frame(main_frame, bg="#121213")
        grid_frame.grid(row=0, column=0, padx=(0, 20))
        side_frame = tk.Frame(main_frame, bg="#121213")
        side_frame.grid(row=0, column=1, sticky="n")
        for r in range(self.max_rows):
            row_cells = []
            row_states = []
            for c in range(self.cols):
                lbl = tk.Label(grid_frame, text="", width=4, height=2, font=("Helvetica", 24, "bold"), bg="#3a3a3c", fg="#ffffff", bd=2, relief="raised")
                lbl.grid(row=r, column=c, padx=4, pady=4)
                lbl.bind("<Button-1>", lambda e, row=r, col=c: self.cycle_feedback(row, col))
                row_cells.append(lbl)
                row_states.append(0)
            self.cells.append(row_cells)
            self.feedback_states.append(row_states)
        tk.Label(side_frame, text="Top 10 candidats", fg="#ffffff", bg="#121213", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.suggestions_box = tk.Listbox(side_frame, bg="#202124", fg="#e8eaed", font=("Consolas", 11), width=22, height=12, activestyle="none")
        self.suggestions_box.grid(row=1, column=0, pady=(4, 10), sticky="n")
        self.suggestions_box.bind("<<ListboxSelect>>", self.on_select_suggestion)
        tk.Label(side_frame, text="Lettres", fg="#ffffff", bg="#121213", font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 0))
        letters_box = tk.Label(side_frame, textvariable=self.letters_var, justify="left", anchor="nw", bg="#202124", fg="#e8eaed", font=("Consolas", 11), width=22, height=5, bd=1, relief="solid")
        letters_box.grid(row=3, column=0, pady=(4, 10), sticky="n")
        controls_frame = tk.Frame(side_frame, bg="#121213")
        controls_frame.grid(row=4, column=0, pady=(10, 0), sticky="w")
        tk.Button(controls_frame, text="Valider feedback", command=self.on_validate_feedback, bg="#538d4e", fg="#ffffff", font=("Helvetica", 11, "bold"), width=18).grid(row=0, column=0, pady=4)
        tk.Button(controls_frame, text="Nouvelle partie", command=self.start_new_game, bg="#3a3a3c", fg="#ffffff", font=("Helvetica", 11), width=18).grid(row=1, column=0, pady=4)

    def start_new_game(self):
        self.remaining_words = list(self.all_words)
        self.guesses = []
        self.green_letters.clear()
        self.yellow_letters.clear()
        self.gray_letters.clear()
        self.current_row = 0
        self.current_guess = None
        self.game_over = False
        for r in range(self.max_rows):
            for c in range(self.cols):
                self.cells[r][c]["text"] = ""
                self.cells[r][c]["bg"] = "#3a3a3c"
                self.feedback_states[r][c] = 0
        self.update_letters_label()
        self.update_suggestions([])
        self.current_guess = random.choice(self.starters)
        self.display_guess()

    def display_guess(self):
        if self.current_guess is None:
            return
        for c in range(self.cols):
            self.cells[self.current_row][c]["text"] = self.current_guess[c].upper()
            self.cells[self.current_row][c]["bg"] = "#3a3a3c"
            self.feedback_states[self.current_row][c] = 0

    def cycle_feedback(self, row, col):
        if row != self.current_row or self.game_over:
            return
        state = (self.feedback_states[row][col] + 1) % 3
        self.feedback_states[row][col] = state
        self.cells[row][col]["bg"] = ["#3a3a3c", "#b59f3b", "#538d4e"][state]

    def on_select_suggestion(self, event):
        if self.game_over:
            return
        selection = self.suggestions_box.curselection()
        if selection:
            idx = selection[0]
            self.current_guess = self.top_list[idx]
            self.display_guess()

    def on_validate_feedback(self):
        if self.game_over or self.current_guess is None:
            return
        pattern = "".join(self.state_to_char(self.feedback_states[self.current_row][c]) for c in range(self.cols))
        self.update_letter_sets(pattern)
        self.remaining_words = [w for w in self.remaining_words if self.matches_pattern(w, self.current_guess, pattern)]
        self.guesses.append((self.current_guess, pattern))
        ranked = self.rank_candidates(self.remaining_words)
        self.update_suggestions(ranked[:10])
        if pattern == "ggggg":
            self.game_over = True
            messagebox.showinfo("Terminé", f"Mot trouvé en {self.current_row + 1} coups.")
            return
        if not ranked:
            self.game_over = True
            messagebox.showwarning("Aucun mot", "Plus aucun mot ne correspond aux contraintes.")
            return
        if self.current_row >= self.max_rows - 1:
            self.game_over = True
            messagebox.showinfo("Fin", "Nombre maximal de tentatives atteint.")
            return
        self.current_row += 1
        self.current_guess = None

    def state_to_char(self, state):
        if state == 2:
            return "g"
        if state == 1:
            return "y"
        return "b"


    def compute_pattern(self, answer, guess):
        result = ["b"] * self.cols
        answer_chars = list(answer)
        for i in range(self.cols):
            if guess[i] == answer[i]:
                result[i] = "g"
                answer_chars[i] = None
        for i in range(self.cols):
            if result[i] == "b":
                ch = guess[i]
                if ch in answer_chars:
                    result[i] = "y"
                    answer_chars[answer_chars.index(ch)] = None
        return "".join(result)

    def matches_pattern(self, word, guess, pattern):
        return self.compute_pattern(word, guess) == pattern

    def rank_candidates(self, candidates):
        if not candidates:
            return []
        if len(candidates) == 1:
            return list(candidates)
        global_counter = Counter()
        pos_counters = [Counter() for _ in range(self.cols)]
        for w in candidates:
            for i, ch in enumerate(w):
                global_counter[ch] += 1
                pos_counters[i][ch] += 1
        scored = []
        for w in candidates:
            seen = set()
            s = 0
            for i, ch in enumerate(w):
                if ch not in seen:
                    s += global_counter[ch]
                    seen.add(ch)
                s += pos_counters[i][ch]
            scored.append((-s, w))
        scored.sort()
        return [w for _, w in scored]

    def update_suggestions(self, top_words):
        self.suggestions_box.delete(0, tk.END)
        self.top_list = top_words[:10]
        for i, w in enumerate(self.top_list, start=1):
            self.suggestions_box.insert(tk.END, f"{i:2d}. {w.upper()}")

    def update_letter_sets(self, pattern):
        guess = self.current_guess
        for i, ch in enumerate(guess):
            p = pattern[i]
            if p == "g":
                self.green_letters.add(ch)
            elif p == "y":
                self.yellow_letters.add(ch)
            elif p == "b":
                if ch not in self.green_letters and ch not in self.yellow_letters:
                    self.gray_letters.add(ch)
        self.update_letters_label()

    def update_letters_label(self):
        green = "".join(sorted(self.green_letters)) or "-"
        yellow = "".join(sorted(self.yellow_letters)) or "-"
        gray = "".join(sorted(self.gray_letters)) or "-"
        self.letters_var.set(f"Vert  : {green}\nJaune : {yellow}\nGris  : {gray}")


if __name__ == "__main__":
    app = WordleAssistant()
    app.mainloop()
