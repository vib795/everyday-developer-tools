"^(\\d{4})-(0[1-9]|1[0-2])-((0[1-9]|1\\d|2[0-8])|(29(?=-0[13-9]|-1[0-2]))|(30(?=-0[13-9]|-1[0-2]))|(31(?=-0[13578]|-1[02]))|(29(?=-02-(?:(?:(?!0000)[0-9]{2}([02468][048]|[13579][26]))-29)))\\s(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\\.\\d{6}$"

Explanation of the pattern:

- `^`: Asserts the start of the string.
- `(\\d{4})`: Matches exactly 4 digits for the year.
- `-`: Matches a hyphen.
- `(0[1-9]|1[0-2])`: Matches a valid month (01 to 12).
- `-`: Matches a hyphen.
- The day part is split into several groups to account for different lengths of months:
    - `(0[1-9]|1\\d|2[0-8])`: Matches days 01-28.
    - `|(29(?=-0[13-9]|-1[0-2]))`: Matches the 29th day for months that are not February.
    - `|(30(?=-0[13-9]|-1[0-2]))`: Matches the 30th day for months that are not February.
    - `|(31(?=-0[13578]|-1[02]))`: Matches the 31st day for months January, March, May, July, August, October, December.
    - `|(29(?=-02-(?:(?:(?!0000)[0-9]{2}([02468][048]|[13579][26]))-29)))`: Matches February 29th in leap years.
- `\\s`: Matches a space.
- `(0[0-9]|1[0-9]|2[0-3])`: Matches a valid hour (00 to 23).
- `:` Matches a colon.
- `([0-5][0-9])`: Matches a valid minute (00 to 59).
- `:` Matches a colon.
- `([0-5][0-9])`: Matches a valid second (00 to 59).
- `\\.`: Matches a dot.
- `\\d{6}`: Matches exactly 6 digits for the fractional seconds.
- `$`: Asserts the end of the string.
This regex should correctly validate dates, including proper handling of the number of days in each month and leap years.