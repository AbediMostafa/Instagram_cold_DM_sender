import subprocess

# Path to the child script
child_script = "t.py"

# Arguments to pass to the child script
try:
    # Run the child script
    result = subprocess.run(
        ["python", child_script],
        text=True,  # Capture output as text
        capture_output=True  # Capture srtdout and stderr
    )

    # Output the results
    print("Child Script Output:")
    print(result.stdout)

    # Check for errors
    if result.returncode != 0:
        print("Error occurred:")
        print(result.stderr)

except Exception as e:
    print(f"An error occurred: {e}")
