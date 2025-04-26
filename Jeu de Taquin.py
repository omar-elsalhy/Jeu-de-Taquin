import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import random
import tkinter as tk
from tkinter import messagebox
import heapq
import time
from itertools import count


def manhattan_distance(cases):
    distance = 0
    for index, case in enumerate(cases):
        if np.all(case == 0):
            continue
        i, j = index // 4, index % 4
        # Trouver la bonne position (dans l'état original)
        for k, c in enumerate(cases):
            if np.array_equal(case, jeu.cases_originales[k]):
                x, y = k // 4, k % 4
                distance += abs(i - x) + abs(j - y)
                break
    return distance

def voisins_et_index(cases, vide_index):
    i, j = vide_index // 4, vide_index % 4
    directions = []
    if i > 0: directions.append((-1, 0))
    if i < 3: directions.append((1, 0))
    if j > 0: directions.append((0, -1))
    if j < 3: directions.append((0, 1))
    voisins = []
    for dx, dy in directions:
        ni, nj = i + dx, j + dy
        idx = ni * 4 + nj
        new_cases = cases.copy()
        new_cases[vide_index], new_cases[idx] = new_cases[idx], new_cases[vide_index]
        voisins.append((new_cases, idx))
    return voisins

def est_termine(cases):
    return all(np.array_equal(cases[i], jeu.cases_originales[i]) for i in range(16))

def serialiser(cases):
    return tuple(np.sum(c) for c in cases)



# Fonction pour charger l'image et la préparer
def charger_image(image_path):
    img = Image.open(image_path).convert('L')  # 'L' pour niveaux de gris
    img = np.array(img)

    # Redimensionner l'image pour qu'elle soit carrée et divisible par 4
    h, w = img.shape
    side_length = max(h, w)
    if side_length % 4 != 0:
        side_length += (4 - side_length % 4)

    img_resized = np.zeros((side_length, side_length), dtype=np.uint8)
    img_resized[:h, :w] = img
    return img_resized



def decouper_image(img):
    n = img.shape[0] // 4
    cases = []
    for i in range(4):
        for j in range(4):
            case = img[i*n:(i+1)*n, j*n:(j+1)*n]
            cases.append(case)
    
    cases[-1] = np.zeros_like(cases[-1])  # La dernière case est vide (noir)
    return cases



#Fonction pour vérifier si le taquin mélangé est soluble
def est_soluble(cases):
    # Transforme chaque case en un nombre représentant son ordre original (sauf la case noire)
    flat = []
    for case in cases:
        if np.all(case == 0):
            flat.append(0)
        else:
            # Utilise une hash simple (la somme des pixels) comme identifiant unique
            flat.append(np.sum(case))

    # Calcule les inversions
    inv_count = 0
    flat_no_zero = [x for x in flat if x != 0]
    for i in range(len(flat_no_zero)):
        for j in range(i+1, len(flat_no_zero)):
            if flat_no_zero[i] > flat_no_zero[j]:
                inv_count += 1

    # Trouver la position de la case vide en partant du bas
    for i, c in enumerate(cases):
        if np.all(c == 0):
            vide_index = i
            break
    ligne_vide = 4 - (vide_index // 4)

    # Règle de solubilité
    return (inv_count + ligne_vide) % 2 == 0



def melanger_cases(cases):
    while True:
        random.shuffle(cases)
        for i, case in enumerate(cases):
            if np.all(case == 0):  # Trouve la case noire
                vide_index = i
                break
        if est_soluble(cases):
            return cases, vide_index



def melanger_cases_mouvements(cases, nb_mouvements=30):
    # On part de l'état résolu
    cases = cases.copy()
    vide_index = 15  # Dernière case vide dans un taquin résolu

    for _ in range(nb_mouvements):
        i, j = vide_index // 4, vide_index % 4
        voisins = []

        # Ajouter les voisins valides
        if i > 0: voisins.append((i - 1, j))
        if i < 3: voisins.append((i + 1, j))
        if j > 0: voisins.append((i, j - 1))
        if j < 3: voisins.append((i, j + 1))

        # Choisir un voisin au hasard
        ni, nj = random.choice(voisins)
        voisin_index = ni * 4 + nj

        # Échanger la case vide avec le voisin
        cases[vide_index], cases[voisin_index] = cases[voisin_index], cases[vide_index]
        vide_index = voisin_index

    return cases, vide_index



class JeuDeTaquin:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Jeu de Taquin")

        self.image_path = image_path
        self.img = charger_image(image_path)
        self.cases = decouper_image(self.img)
        self.cases_originales = self.cases.copy()#Copie pour comparaison si taquin résolu
        #self.cases, self.vide_index = melanger_cases(self.cases)
        #self.vide_index = 15  # La dernière case est vide au début (index 15)
        self.cases, self.vide_index = melanger_cases_mouvements(self.cases_originales, nb_mouvements=50)

        
        # Créer un canevas pour afficher les cases
        self.canvas = tk.Canvas(self.root, width=self.img.shape[0], height=self.img.shape[1])
        self.canvas.pack()

        self.images = []   # Stockage des PhotoImage pour éviter qu’elles soient supprimées
        self.buttons = {}  # Pour les rectangles cliquables

        bouton_restart = tk.Button(self.root, text="🔄 Recommencer", command=self.recommencer)
        bouton_restart.pack(pady=5)

        btn_resoudre = tk.Button(self.root, text="🧠 Résoudre", command=self.resoudre)
        btn_resoudre.pack(pady=10)
        
        self.afficher_cases()

    def afficher_cases(self):
        n = self.img.shape[0] // 4
        self.images = []  # Reset des images à chaque appel pour éviter les duplicatas

        for i in range(4):
            for j in range(4):
                index = i * 4 + j
                case = self.cases[index]
                x1, y1 = j * n, i * n
                x2, y2 = (j + 1) * n, (i + 1) * n

                # 🔁 Convertir la case en image PIL puis PhotoImage
                image_case = Image.fromarray(case)
                photo = ImageTk.PhotoImage(image_case)
                self.images.append(photo)  # Important : stocker la référence

                # 🖼️ Afficher l'image (y compris la case vide, qui est toute noire)
                self.canvas.create_image((x1 + x2) // 2, (y1 + y2) // 2, image=photo)

                # 🎯 Si ce n'est pas la case vide, rendre la zone interactive
                if index != self.vide_index:
                    rect = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="", fill="", tags="button"
                    )
                    self.buttons[(i, j)] = rect
                    self.canvas.tag_bind(
                        rect, '<Button-1>',
                        lambda event, index=index: self.deplacer_case(index)
                    )

    def deplacer_case(self, index):
        vide_i, vide_j = self.vide_index // 4, self.vide_index % 4
        case_i, case_j = index // 4, index % 4

        # Vérifier si la case est adjacente à la case vide
        if abs(case_i - vide_i) + abs(case_j - vide_j) == 1:
            # Échanger les cases
            self.cases[self.vide_index], self.cases[index] = self.cases[index], self.cases[self.vide_index]
            self.vide_index = index
            self.canvas.delete("all")
            self.afficher_cases()

            # Vérifier si l'image est reconstituée
            # Utiliser np.array_equal pour comparer les tableaux
            if all(np.array_equal(self.cases[i], self.cases_originales[i]) for i in range(len(self.cases))):
                messagebox.showinfo("Gagné", "Félicitations, vous avez reconstitué l'image !")

    def recommencer(self):
        self.cases = decouper_image(self.img)
        self.cases, self.vide_index = melanger_cases_mouvements(self.cases_originales, nb_mouvements=50)
        self.canvas.delete("all")
        self.afficher_cases()
    
    def resoudre(self):
        compteur = count()
        debut = time.time()
        depart = self.cases
        vide = self.vide_index

        visite = set()
        #queue = [(manhattan_distance(depart), 0, depart, vide, [])]  # (heuristique, profondeur, état, vide_index, chemin)
        queue = [(manhattan_distance(depart), next(compteur), 0, depart, vide, [])]

        while queue:
            _, _, profondeur, etat, vide, chemin = heapq.heappop(queue)

            if est_termine(etat):
                print("Solution trouvée en", len(chemin), "étapes, durée", round(time.time() - debut, 2), "s")
                self.afficher_solution(chemin)
                return

            code = serialiser(etat)
            if code in visite:
                continue
            visite.add(code)

            for voisin, new_vide in voisins_et_index(etat, vide):
                heapq.heappush(queue, (
                manhattan_distance(voisin) + profondeur + 1,  # priorité
                next(compteur),                              # compteur unique
                profondeur + 1,
                voisin,
                new_vide,
                chemin + [(voisin, new_vide)]
            ))


    
    def afficher_solution(self, chemin):
        if not chemin:
            return

        prochain, new_vide = chemin[0]
        self.cases = prochain
        self.vide_index = new_vide
        self.canvas.delete("all")
        self.afficher_cases()

        self.root.after(1000, lambda: self.afficher_solution(chemin[1:]))  # 1 mouvement/sec





# Créer l'application Tkinter
root = tk.Tk()
jeu = JeuDeTaquin(root, "simba.png")  # Mettre ici le chemin de l'image
root.mainloop()
