#!/bin/bash

# ./PuzzleCrypt => pour lancer le script

# Vérification que 7z est installé
if ! command -v 7z &> /dev/null; then
    echo "Erreur : 7z (p7zip) n'est pas installé. Installez-le avec 'sudo apt install p7zip' ou équivalent."
    exit 1
fi

# Fonction pour générer un nombre entre 4 et 255 basé sur un mot de passe
generate_n() {
    local password="$1"
    local sum=0
    for ((i=0; i<${#password}; i++)); do
        sum=$((sum + $(printf "%d" "'${password:$i:1}")))  # Somme des codes ASCII
    done
    n=$(( (sum % 252) + 4 ))  # n est compris entre 4 et 255
    echo "$n"
}

# Fonction pour permuter et renommer les blocs
permute_and_rename() {
    local password="$1"
    local dir="$2"
    local files=($(ls "$dir" | grep "\.7z\."))
    local seed=$(echo -n "$password" | cksum | cut -f1 -d' ')
    local num_files=${#files[@]}

    # Générer une permutation basée sur le mot de passe
    local indices=($(seq 0 $((num_files-1))))
    for ((i=num_files-1; i>0; i--)); do
        local j=$(( (seed + i) % (i+1) ))
        local tmp=${indices[i]}
        indices[i]=${indices[j]}
        indices[j]=$tmp
    done

    # Renommer les fichiers selon la permutation
    for ((i=0; i<num_files; i++)); do
        local old_name="${files[i]}"
        local new_name="${dir}/part_$((indices[i]+1)).7z"
        mv "$dir/$old_name" "$new_name"
    done
}

# Fonction pour restaurer l'ordre des blocs
restore_order() {
    local password="$1"
    local dir="$2"
    local files=($(ls "$dir" | grep "^part_[0-9]\+\.7z$"))
    local seed=$(echo -n "$password" | cksum | cut -f1 -d' ')
    local num_files=${#files[@]}

    # Générer la permutation inverse
    local indices=($(seq 0 $((num_files-1))))
    for ((i=num_files-1; i>0; i--)); do
        local j=$(( (seed + i) % (i+1) ))
        local tmp=${indices[i]}
        indices[i]=${indices[j]}
        indices[j]=$tmp
    done

    # Créer un tableau pour l'ordre inverse
    local reverse_indices=($(seq 0 $((num_files-1))))
    for ((i=0; i<num_files; i++)); do
        reverse_indices[${indices[i]}]=$i
    done

    # Renommer les fichiers pour restaurer l'ordre
    for ((i=0; i<num_files; i++)); do
        local old_name="${files[i]}"
        local new_name="${dir}/part_$((reverse_indices[i]+1)).7z"
        mv "$dir/$old_name" "$new_name"
    done
}

# Fonction pour chiffrer et découper
encrypt_and_split() {
    local input_file="$1"
    local password1="$2"
    local output_dir="$3"
    local n=$(generate_n "$password1")

    echo "Découpage et chiffrement avec le mot de passe 1..."
    7z a -v"$n"m -p"$password1" -mhe=on "$output_dir/temp_split.7z" "$input_file" > /dev/null

    # Permuter et renommer les blocs
    permute_and_rename "$password1" "$output_dir"
}

# Fonction pour rassembler et chiffrer
assemble_and_encrypt() {
    local output_dir="$1"
    local password2="$2"
    local final_output="$3"

    echo "Assemblage et chiffrement avec le mot de passe 2..."
    7z a -p"$password2" -mhe=on "$final_output" "$output_dir"/part_*.7z > /dev/null
}

# Fonction pour déchiffrer et restaurer
decrypt_and_restore() {
    local encrypted_file="$1"
    local password2="$2"
    local output_dir="$3"
    local password1="$4"

    echo "Déchiffrement avec le mot de passe 2..."
    7z x -p"$password2" -o"$output_dir" "$encrypted_file" > /dev/null

    # Restaurer l'ordre des blocs
    restore_order "$password1" "$output_dir"

    # Déchiffrer et rassembler avec le mot de passe 1
    echo "Rassemblement et déchiffrement avec le mot de passe 1..."
    7z x -p"$password1" -o"$output_dir" "$output_dir"/part_1.7z > /dev/null
}

# Menu principal
echo "PuzzleCrypt - Chiffrement avancé avec 7z"
echo "1. Chiffrer un fichier"
echo "2. Déchiffrer un fichier"
read -p "Choisissez une option (1 ou 2) : " option

if [ "$option" = "1" ]; then
    read -p "Fichier à chiffrer : " input_file
    read -s -p "Mot de passe 1 (pour découper/chiffrer) : " password1
    echo
    read -s -p "Mot de passe 2 (pour l'archive finale) : " password2
    echo
    read -p "Dossier de sortie (ex: ./output) : " output_dir

    mkdir -p "$output_dir"
    encrypt_and_split "$input_file" "$password1" "$output_dir"
    assemble_and_encrypt "$output_dir" "$password2" "${output_dir}/final.7z"
    echo "Chiffrement terminé. Archive finale : ${output_dir}/final.7z"

elif [ "$option" = "2" ]; then
    read -p "Archive à déchiffrer : " encrypted_file
    read -s -p "Mot de passe 2 (pour l'archive finale) : " password2
    echo
    read -s -p "Mot de passe 1 (pour rassembler/déchiffrer) : " password1
    echo
    read -p "Dossier de sortie (ex: ./output) : " output_dir

    mkdir -p "$output_dir"
    decrypt_and_restore "$encrypted_file" "$password2" "$output_dir" "$password1"
    echo "Déchiffrement terminé. Fichier restauré dans : $output_dir"
else
    echo "Option invalide."
    exit 1
fi
