import blessed

term = blessed.Terminal()

print(f"{term.home}{term.black_on_skyblue}{term.clear}")
print("press 'q' to quit.")
with term.cbreak():
    val = ''
    while val.lower() != 'q':
        val = term.inkey()
        if val.is_sequence:
           print(f"got sequence: {[str(val)]}, name={val.name}, code={val.code}")
        elif val:
           print(f"not seq: {[str(val)]} code={val.code} name={val.name}")
    print(f'bye! {term.normal}')