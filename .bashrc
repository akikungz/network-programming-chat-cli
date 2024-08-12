# Check if git bash on windows
if [ -n "$WINDIR" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi