import tkinter as tk
from ui import EightRooksApp
from algorithms import (
    DFSAlgorithm,
    BFSAlgorithm,
    UCSAlgorithm,
    IDSAlgorithm,
    IDSStarAlgorithm,
    HillClimbingAlgorithm,
    SimulatedAnnealingAlgorithm,
    BacktrackingAlgorithm,
    BeamSearchAlgorithm,
    BacktrackingForwardAlgorithm,
    BacktrackingAC3Algorithm,
    GeneticAlgorithm,
    AStarAlgorithm,
    GreedyBestFirstAlgorithm,
    PartiallyObservableSearchAlgorithm,
    NoObservationSearchWithBeliefDFS,
    AndOrSearchAlgorithm
)
def main():
    root = tk.Tk()
    algorithms_dict = {
        "DFS": DFSAlgorithm,
        "BFS": BFSAlgorithm,
        "UCS": UCSAlgorithm,
        "IDS": IDSAlgorithm,
        "IDS*": IDSStarAlgorithm,
        "A*": AStarAlgorithm,
        "GREEDY": GreedyBestFirstAlgorithm,
        "HC": HillClimbingAlgorithm,
        "BEAM": BeamSearchAlgorithm,
        "GA": GeneticAlgorithm,
        "SA":SimulatedAnnealingAlgorithm,
        "BATR":BacktrackingAlgorithm,
        "BT+FC": BacktrackingForwardAlgorithm,
        "BT+AC3":BacktrackingAC3Algorithm,
        "PO-DFS": PartiallyObservableSearchAlgorithm,
        "NO-OBS(DFS)": NoObservationSearchWithBeliefDFS,
        "AND-OR": AndOrSearchAlgorithm,

    }
    app = EightRooksApp(root, algorithms_dict, default_algo="DFS")
    root.mainloop()

if __name__ == "__main__":
    main()
