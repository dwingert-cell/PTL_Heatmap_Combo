import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from matplotlib.colors import LinearSegmentedColormap
Top = [
    "F1","R1","F2","R2","F3","R3","F4","R4",
    "F5","R5","F6","R6","F7","R7","F8","R8",
    "F9","R9","F10","R10","F11","R11","F12","R12",
    "F13","R13","F14","R14","F15","R15","F16","R16",

    "F17","R17","F18","R18","F19","R19","F20","R20",
    "F21","R21","F22","R22","F23","R23","F24","R24",
    "F25","R25","F26","R26","F27","R27","F28","R28",
    "F29","R29","F30","R30","F31","R31","F32","R32",
]



TopS = [
    "FS1","RS1","FS2","RS2",
    "FS3","RS3","FS4","RS4",
    "RS5","FS5","FS6","RS6",
    "FS7","RS7","FS8","RS8",
    "FS9","RS9","FS10","RS10",
    "FS11","RS11","FS12","RS12",
    "FS13","RS13","FS14","RS14",
    "FS15","RS15","FS16","RS16",

    "FS17","RS17","FS18","RS18",
    "FS19","RS19","FS20","RS20",
    "FS21","RS21","FS22","RS22",
    "FS23","RS23","FS24","RS24",
    "FS25","RS25","FS26","RS26",
    "FS27","RS27","FS28","RS28",
    "FS29","RS29","FS30","RS30",
    "FS31","RS31","FS32","RS32"
]


Bottom = [
    "R64","F64","R63","F63","R62","F62","R61","F61",
    "R60","F60","R59","F59","R58","F58","R57","F57",
    "R56","F56","R55","F55","R54","F54","R53","F53",
    "R52","F52","R51","F51","R50","F50","R49","F49",
    
    "R48","F48","R47","F47","R46","F46","R45","F45",
    "R44","F44","R43","F43","R42","F42","R41","F41",
    "R40","F40","R39","F39","R38","F38","R37","F37",
    "R36","F36","R35","F35","R34","F34","R33","F33",

]

BottomS = [
    "RS64", "FS64", "RS63", "FS63",
    "RS62", "FS62", "RS61", "FS61",
    "RS60", "FS60", "RS59", "FS59",
    "RS58", "FS58", "RS57", "FS57",
    "RS56", "FS56", "RS55", "FS55",
    "RS54", "FS54", "RS53", "FS53",
    "RS52", "FS52", "RS51", "FS51",
    "RS50", "FS50", "RS49", "FS49",
    
    "RS48", "FS48", "RS47", "FS47",
    "RS46", "FS46", "RS45", "FS45",
    "RS44", "FS44", "RS43", "FS43",
    "RS42", "FS42", "RS41", "FS41",
    "RS40", "FS40", "RS39", "FS39",
    "RS38", "FS38", "RS37", "FS37",
    "RS36", "FS36", "RS35", "FS35",
    "RS34", "FS34", "RS33", "FS33"

]


Top = Top + TopS
Bottom = BottomS + Bottom 


colors = [
    (0, 0, 1),       # deep blue
    (0.3, 0.3, 1),   # intermediate blue
    (0.6, 0.6, 1),   # light blue
    (1, 1, 1),       # white
    (1, 0.6, 0.6),   # light red
    (1, 0.3, 0.3),   # intermediate red
    (1, 0, 0)        # full red
]



nodes = [0.0, 1.0/6.0, 2.0/6.0, 3.0/6.0, 4.0/6.0, 5.0/6.0, 1.0]
custom_cmap = LinearSegmentedColormap.from_list("custom_red_extended", list(zip(nodes, colors)))

def display_matrix(cable):
    matrix = np.array(cable.matrix, dtype=np.float64)
    print(matrix)
    matrix1 = matrix[0].reshape(1, -1)  
    matrix2 = matrix[1].reshape(1, -1)
    sn = cable.serial_number

    fig, axes = plt.subplots(3, 1, figsize=(24, 8), 
                             gridspec_kw={'height_ratios': [1, 0.1, 1]})
    fig.suptitle(f'Heatmap for cable with SN: {sn}', fontsize=20)

    # Plot first heatmap with color bar
    
# Plot first heatmap
    sns.heatmap(matrix1, ax=axes[0], cmap=custom_cmap, annot=False, square=False,
                xticklabels=Top, yticklabels=[''], cbar=True, cbar_kws={'label': 'Intensity'},
                vmin=0.0, vmax=6.0)

    # Leave middle subplot blank
    axes[1].axis('off')

    # Plot second heatmap
    sns.heatmap(matrix2, ax=axes[2], cmap=custom_cmap, annot=False, square=False,
                xticklabels=Bottom, yticklabels=[''], cbar=True, cbar_kws={'label': 'Intensity'},
                vmin=0.0, vmax=6.0)


    # Adjust layout to make room for the title
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    st.pyplot(plt)