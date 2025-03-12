#main.py
# FUNCTIONS ================================================== #

from connect_email import connect_to_gmail
from connect_email import fetch_uber_receipts_by_month
from get_env import get_env


# CORE ======================================================= #
def main():
    
    my_email = get_env("MY_EMAIL")
    my_password = get_env("IMAP_KEY")

    g_mail = connect_to_gmail(my_email, my_password)

    # Defina o mês e ano para a busca (por exemplo, abril de 2021)
    month = 2   # Abril
    year = 2025
    
    print(f"\nBuscando emails de recibos do Uber para {month}/{year}...\n")
    fetch_uber_receipts_by_month(g_mail, month, year, search_term="Uber")

    # Fecha a conexão
    g_mail.logout()

if __name__ == '__main__':
    main()