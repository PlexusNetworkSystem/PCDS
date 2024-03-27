#!/bin/bash

# Define the set of characters including both alphabets and digits
characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Generate a random string of a specified length
generate_random_string() {
    local length=$1
    local random_string=""
    for ((i=0; i<length; i++)); do
        random_index=$((RANDOM % ${#characters}))
        random_char="${characters:$random_index:1}"
        random_string="$random_string$random_char"
    done
    echo "$random_string"
}

# Example usage: generate a random string of length 100
random_string=$(generate_random_string 100)
echo "$random_string"
