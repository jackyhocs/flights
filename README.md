# Skypath

## Backend Notes
* Flake8 is used for enforcing style and consistency
* There is a typo in "JFK" for flight SP995, I have decided to rename this to the corrected version instead of throwing a warning and not logging this.We may want to throw a warning instead, but I currently prefer just making the change since this is a small dataset and having one more available flight may affect test cases.