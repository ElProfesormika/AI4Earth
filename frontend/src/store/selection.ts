import { create } from "zustand";

interface State {
  selectedBin: number | null;
  setSelectedBin: (id: number | null) => void;
}

export const useSelectionStore = create<State>((set) => ({
  selectedBin: null,
  setSelectedBin: (id) => set({ selectedBin: id }),
}));
