#!/bin/bash

echo "========================================"
echo "Lancement du jeux SuperMarioBros3 like !"
echo "  Developer par CHRZASZCZ Naulan."
echo "  Crée le 26/09/2020 à 8h35"
echo "========================================"
echo
echo "========================================"
echo "N'hesite pas a faire un tour sur mon site Web !"
echo "https://www.chrz-developments.com/"
echo "========================================"

# Texts
wrongPythonVersion="ERREUR: La version de Python n'est pas valide !"
pythonVersionRequired="  Veuillez installer la version 3.7.7 ou plus elevé."
dontHavePython="Avez-vous Python installer ? [O/n] > "
falseInstalling="Vous avez mit non pour l'installation de Python"

# Get Python version
echo "Verification de l'existence potencielle de Python..."
python_version=$(python3 --version 2> /dev/null)
if [ $? -ne 0 ]; then
  python_version=$(python --version 2> /dev/null)
  if [ $? -ne 0 ]; then
    # Propose to install Python
    read -p "$dontHavePython" choix
    if [ choix == "O" ]; then
      export DEBIAN_FRONTEND=noninteractive
      apt-get -yq install python3
    else
      echo "$falseInstalling"
      exit 1
fi; fi; fi
python_version=$(echo "$python_version" | cut -d' ' -f2)
echo "Verification terminée !"
# Finish the got Python version

function errorPythonVersion() {
  echo "$wrongPythonVersion"
  echo "  Vous avez sur votre machine la version: $python_version"
  echo "$pythonVersionRequired"
}

# Check Python version
echo "Verification de la version de Python courante..."
# Check first number in python version (x.3.3)
firstNumber=$(echo "$python_version" | cut -d'.' -f1 2> /dev/null)
if [ "$firstNumber" != "3" ]; then
  errorPythonVersion
  exit 2
else
  # ...secondNumber (3.x.3)
  secondNumber=$(echo "$python_version" | cut -d'.' -f2 2> /dev/null)
  if [ "$secondNumber" -lt 7 ]; then
    errorPythonVersion
    exit 2
  else
    # ...lastNumber (3.3.x)
    lastNumber=$(echo "$python_version" | cut -d'.' -f3 2> /dev/null)
    if (($lastNumber < 7 & $secondNumber < 7)); then
      errorPythonVersion
      exit 2
fi; fi
  echo "Verification terminée ! Vous avez Python $python_version (La version minimal est Python 3.7.7)"
  # End check Python version

  python3 -m pip list | grep -o "pygame" >> /dev/null
  if (( $? != 0 & $? != 127 )); then
    echo "WARNING: La librairie 'pygame' n'existe pas."
    echo "  Une installation de la librairie va suivre !"
    python3 -m pip install --no-input pygame
  else
    if [ $? == 127 ]; then
      python -m pip install --no-input pygame
fi; fi

  python3 './SuperMarioBros3.pyw' > "console.log"
  if [ $? -ne 0 ]; then
    python './SuperMarioBros3.pyw' > "console.log"
    if [ $? -ne 0 ]; then
      echo "ERREUR: Le jeux n'a pas pu êtres lancée !"
      exit 3
fi; fi; fi
exit 0
