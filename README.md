## Jeu de Taquin en Python
Il s'agit pour ce TP de programmer un jeu de taquin (https://fr.wikipedia.org/wiki/Taquin).

Nous partons d'une image, que nous mettons en niveaux de gris, que nous rendons carrée (hauteur = largeur), dont la hauteur (et donc la largeur sera un multiple de 4, dont le carreau en bas à droite sera mis en noir (case vide), puis dont les carreaux seront mélangés.

L'image est ensuite affichée. Le joueur donne alors une action, qui consiste à déplacer la case vide (c'est à dire, l'échanger avec une des cases adjacente), et ainsi de suite, tant que l'image d'origine n'est pas reconstituée.

### Evolutions possibles
- S'assurer que le jeu présenté au joueur est soluble (voir la page wikipédia)
- Utiliser TKinter pour l'interface graphique (ou même que pour l'affichage de l'image, voir https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html#sphx-glr-gallery-user-interfaces-embedding-in-tk-sgskip-py pour l'intégration matplotlib/tkinter)
- Proposer un algo qui résout le taquin
