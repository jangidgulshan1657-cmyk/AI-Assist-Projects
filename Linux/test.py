x = 12.3456

# Formated string with type float!! 
# fixed-point float
print(f"{x:.0f}")  # No decimal
print(f"{x:.1f}")  # 1 decimal Allowed
print(f"{x:.2f}")  # 2 decimal places Rounded
print(f"{x:.3f}")  # 3 decimal places Rounded


#:> or < aligns the text in right or left side with specified Columns!
name = "video.mp4"
size = "1.5 MB"

# Left-align in a 12-char column, right-align in a 9-char column:
print(f"|{name:<12}|{size:>9}|")
# Output: |video.mp4   |   1.5 MB|


# You can Also Combine them!!
num = 4.2

# Right-aligned, total box width of 9, rounded to 1 decimal place:
print(f"[{num:>9.1f}]")
# Output: [      4.2]  (6 spaces + 3 characters for "4.2" = 9 total)