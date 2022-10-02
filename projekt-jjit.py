import json
import requests
import pandas as pd
import re


url_jj = "https://justjoin.it/api/offers" # Downloading data from JustJoin and loading as a JSON.
r_jj = requests.get(url_jj)
unsorted_data_jj = json.loads(r_jj.text)

url_rj = "https://api.rocketjobs.pl/v2/user-panel/offers?" # Downloading data from RocketJobs and loading as a JSON.
r_rj = requests.get(url_rj)
unsorted_data_rj = json.loads(r_rj.text)


cat_id = { # It's for RocketJobs offers.
    "recruitment": 31,
    "marketing":2,
    "public_relations":5,
    "sales":8,
    "accountant":11,
    "graphic_designer":26,
    "ux_ui":28,
    "HR_leadership":32,
    "HR_office": 33,
    "HR_research": 34,
    "EB": 35,
    "payroll":36,
}


def create_df(tech, exp, sorted_data):
    """This function takes data from another function for JustJoin offers. 
    It's tech, experience and sorted data. Sorted data is a list which
    contains element with choosen tech and category.
    
        Parameters:
            tech (str): A string with chosen technology
            exp (str): A string with chosen experience (posiible are: junior, mid, senior)
            sorted_data (list): A list with sorted elements for chosen experience and technology
            
        Returns:
            Function creates csv file."""

    info_set = set() # This way the programme won't have the same offers from the same company in a different cities.

    for item in sorted_data:
        empl_type = item["employment_types"]
        for i in empl_type:
            if i["type"] == "b2b":
                try:
                    if i["salary"]["currency"] == "pln":
                        info = item["company_name"], i["salary"]["from"], i["salary"]["to"], item["title"]
                        info_set.add(info)

                except TypeError: # The function uses it so it doesn't show offers without salary.
                    continue

    df = pd.DataFrame(info_set, columns=["Company", "Salary from", "Salary to", "Title"])
    df.to_csv("C:/Users/marty/Desktop/jjit/{}_{}.csv".format(tech,exp), index=False)


def offer(tech, exp):
    """It's main function for JustJoin offers. It sorts data and gives
    input to another function to make csv file.
    
        Parameters:
            tech (str): A string with chosen technology
            exp (str): A string with chosen experience (posiible are: junior, mid, senior)
            
        Returns:
            sorted_data (list): A list containing chosen job offers."""

    sorted_data = []

    if tech == "flutter": # API doesn't show this technology in one of main categories, so it's best to sort it this way.
        for item in unsorted_data_jj:
            if re.search("Flutter", item["title"]) and (item["experience_level"] == exp):
                sorted_data.append(item)

    elif tech == "wordpress": # This is the same situation as in flutter.
        for item in unsorted_data_jj:
            if re.search("Wordpress", item["title"]) and (item["experience_level"] == exp):
                sorted_data.append(item)
        
    else:
        for item in unsorted_data_jj:
            if (item["marker_icon"] == tech) and (item["experience_level"] == exp):
                sorted_data.append(item)
                
    create_df(tech, exp, sorted_data)


def permanent_to_b2b(salary):
    """This function calculates salary from employment contract to
    b2b from RocketJobs offers. It uses external calculator. In the long URL 
    there are put braces and with string format it takes the original data
    from function input. It's used in another function.
    
    Parameters:
        salary (int): A salary integer for a job with employment contract
        
    Returns:
        output (float): Salary calculated to b2b."""

    url= "https://www.money.pl/api/graphql?query=query%20sg_money_gielda_kalulator_wynagrodzen(%24rok_podatkowy%3A%20Int!%2C%20%24typ_kalkulatora%3A%20Podatki_CalculatorTypesEnum!%2C%20%24typ_wynagrodzenia%3A%20Podatki_SalaryTypesEnum!%2C%20%24pensja%3A%20Float!%2C%20%24pensja_miesiace%3A%20%5BFloat%5D%2C%20%24koszty_autorskie%3A%20Int%2C%20%24koszty_autorskie_procent%3A%20Int%2C%20%24ppk%3A%20Int%2C%20%24ppk_pracownik%3A%20Float%2C%20%24ppk_pracodawca%3A%20Float%2C%20%24pit_26%3A%20Int%2C%20%24zwiekszone_koszty_uzyskania%3A%20Int%2C%20%24poza_miejscem_zamieszkania%3A%20Int%2C%20%24uwzglednij_kwote_wolna%3A%20Int%2C%20%24wspolne_rozliczanie%3A%20Int)%20%7B%0A%20%20calculated%3A%20salary_calc(rok_podatkowy%3A%20%24rok_podatkowy%2C%20typ_kalkulatora%3A%20%24typ_kalkulatora%2C%20typ_wynagrodzenia%3A%20%24typ_wynagrodzenia%2C%20pensja%3A%20%24pensja%2C%20pensja_miesiace%3A%20%24pensja_miesiace%2C%20koszty_autorskie%3A%20%24koszty_autorskie%2C%20koszty_autorskie_procent%3A%20%24koszty_autorskie_procent%2C%20ppk%3A%20%24ppk%2C%20ppk_pracownik%3A%20%24ppk_pracownik%2C%20ppk_pracodawca%3A%20%24ppk_pracodawca%2C%20pit_26%3A%20%24pit_26%2C%20zwiekszone_koszty_uzyskania%3A%20%24zwiekszone_koszty_uzyskania%2C%20poza_miejscem_zamieszkania%3A%20%24poza_miejscem_zamieszkania%2C%20uwzglednij_kwote_wolna%3A%20%24uwzglednij_kwote_wolna%2C%20wspolne_rozliczanie%3A%20%24wspolne_rozliczanie)%20%7B%0A%20%20%20%20miesiace%20%7B%0A%20%20%20%20%20%20miesiac%0A%20%20%20%20%20%20koszt_uzyskania%0A%20%20%20%20%20%20zaliczka%0A%20%20%20%20%20%20zdrowotne%0A%20%20%20%20%20%20chorobowe%0A%20%20%20%20%20%20rentowe%0A%20%20%20%20%20%20emerytalne%0A%20%20%20%20%20%20rentowe_pracodawca%0A%20%20%20%20%20%20emerytalne_pracodawca%0A%20%20%20%20%20%20brutto%0A%20%20%20%20%20%20netto%0A%20%20%20%20%20%20stawka%0A%20%20%20%20%20%20zaliczka%0A%20%20%20%20%20%20koszt_pracodawcy%0A%20%20%20%20%20%20wypadkowe_pracodawca%0A%20%20%20%20%20%20fundusz_pracy_pracodawca%0A%20%20%20%20%20%20fgsp_pracodawca%0A%20%20%20%20%20%20__typename%0A%20%20%20%20%7D%0A%20%20%20%20koszt_uzyskania%0A%20%20%20%20zaliczka%0A%20%20%20%20zdrowotne%0A%20%20%20%20chorobowe%0A%20%20%20%20rentowe%0A%20%20%20%20emerytalne%0A%20%20%20%20rentowe_pracodawca%0A%20%20%20%20emerytalne_pracodawca%0A%20%20%20%20zaliczka%0A%20%20%20%20netto%0A%20%20%20%20brutto%0A%20%20%20%20niedoplata%0A%20%20%20%20koszt_pracodawcy%0A%20%20%20%20fgsp_pracodawca%0A%20%20%20%20wypadkowe_pracodawca%0A%20%20%20%20fundusz_pracy_pracodawca%0A%20%20%20%20zlecenie_netto_miesiac%0A%20%20%20%20zlecenie_brutto_miesiac%0A%20%20%20%20zlecenie_pracodawca_miesiac%0A%20%20%20%20dzielo_netto_miesiac%0A%20%20%20%20dzielo_brutto_miesiac%0A%20%20%20%20dzielo_pracodawca_miesiac%0A%20%20%20%20praca_netto_miesiac%0A%20%20%20%20praca_brutto_miesiac%0A%20%20%20%20praca_pracodawca_miesiac%0A%20%20%20%20__typename%0A%20%20%7D%0A%7D%0A&operationName=sg_money_gielda_kalulator_wynagrodzen&variables=%7B%22rok_podatkowy%22%3A2022%2C%22pensja%22%3A{}%2C%22typ_kalkulatora%22%3A%22UMOWA_O_PRACE%22%2C%22typ_wynagrodzenia%22%3A%22brutto%22%2C%22koszty_autorskie%22%3A0%2C%22koszty_autorskie_procent%22%3A0%2C%22poza_miejscem_zamieszkania%22%3A0%2C%22wspolne_rozliczanie%22%3A0%2C%22uwzglednij_kwote_wolna%22%3A1%2C%22ppk%22%3A0%2C%22ppk_pracownik%22%3A2%2C%22ppk_pracodawca%22%3A1.5%2C%22pit_26%22%3A0%7D".format(salary)

    r = requests.get(url)

    raw_data = json.loads(r.text)

    el = raw_data["data"]["calculated"]["miesiace"]
    return el[0]["koszt_pracodawcy"]


def rj_offer(position, exp):
    """This is the main function for RocketJob offers. It sorts expected data to
    set. When offer shows salary only for permanent contract, it uses another
    function to calculate it to b2b.
    
        Parameters:
            position (str): A string with chosen job category
            exp (str): A string with chosen experience (posiible are: junior, mid, senior)
            
        Returns:
            Function creates csv file."""

    info_set = set()

    for item in unsorted_data_rj["data"]:
        if (item["categoryId"] == cat_id[position]) and (item["experienceLevel"] == exp):

            empl_type = item["employmentTypes"]
            for i in empl_type:
                if i["currency"] == "pln" and i["from"] != None: 
                        
                    if i["type"] == ("b2b" or "any"):

                        info = item["companyName"], i["from"], i["to"], item["title"]
                        info_set.add(info)

                    else:

                        salary_from = permanent_to_b2b(i["from"])
                        salary_to = permanent_to_b2b(i["to"])

                        info = item["companyName"], salary_from, salary_to, item["title"]
                        info_set.add(info)


    df = pd.DataFrame(info_set, columns=["Company", "Salary from", "Salary to", "Title"])
    df.to_csv("C:/Users/marty/Desktop/jjit/{}_{}.csv".format(position,exp), index=False)                    

    print(info_set)

"""rj_offer("recruitment", "mid")
offer("ruby", "senior")
offer("wordpress", "senior")"""