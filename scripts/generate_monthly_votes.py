import click
from datetime import datetime

from re import sub

CURRENT_YEAR = datetime.now().year


# Define a function to convert a string to camel case
def camel_case(s):
    # Use regular expression substitution to replace underscores and hyphens with spaces,
    # then title case the string (capitalize the first letter of each word), and remove spaces
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")

    # Join the string, ensuring the first letter is lowercase
    return ''.join([s[0].lower(), s[1:]])


@click.command()
@click.option('--from_month', required=True, help='from 3-char month')
@click.option('--to_month', required=True, help='to 3-char month')
@click.option('--from_years', default=CURRENT_YEAR, help='from years')
@click.option('--to_years', default=CURRENT_YEAR, help='to years')
@click.option('--sktls', required=True, help='amount of sktl')
def cli(from_month, to_month, from_years, to_years, sktls):
    print("TITLE")
    print()
    print(f"Space Actions/SKTLs Generation DAO Vote For {from_month.capitalize()} 6, {from_years} "
          f"through {to_month.capitalize()} 5, {to_years}")

    print()
    print()
    print("BODY")
    print()
    print(f'The SKTLs team of volunteers proposes to generate {sktls} SKTL tokens. '
          'If you are a SKTL token holder, '
          'please vote "yes" or "no, more reviews are needed" on this token generation proposal. '
          'Reference: https://sktls.com/?page_id=1278')


if __name__ == '__main__':
    cli()
