import tkinter as tk
from ui.gui import EightRooksApp
from algorithms.dfs import DFSAlgorithm

def main():
    root = tk.Tk()
    algo = DFSAlgorithm()   # Có thể đổi BFSAlgorithm() sau này
    app = EightRooksApp(root, algo)
    root.mainloop()

if __name__ == "__main__":
    main()
