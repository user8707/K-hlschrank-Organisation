import streamlit as st
import pandas as pd
from github_contents import GithubContents
from PIL import Image

# Set constants for user registration
DATA_FILE = "FreshAlert-Registration.csv"
DATA_COLUMNS = ["Vorname", "Nachname", "E-Mail", "Passwort", "Passwort wiederholen"]

# Set constants for fridge contents
DATA_FILE_FOOD = "Kühlschrankinhalt.csv"
DATA_COLUMNS_FOOD = ["UserID", "Lebensmittel", "Kategorie", "Lagerort", "Standort", "Ablaufdatum"]

# Load the image
image = Image.open('images/Logo_Freshalert-Photoroom.png')

# Resize the image
small_image = image.resize((90, 105))

# Set page configuration
st.set_page_config(
    page_title="FreshAlert",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_github():
    """Initialize the GithubContents object and other session state variables."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"]
        )

    # Initialize settings_enabled attribute
    if 'settings_enabled' not in st.session_state:
        st.session_state.settings_enabled = True


def init_dataframe_login():
    """Initialize or load the dataframe for user registration."""
    if 'df_login' not in st.session_state:
        if st.session_state.github.file_exists(DATA_FILE):
            st.session_state.df_login = st.session_state.github.read_df(DATA_FILE)
        else:
            st.session_state.df_login = pd.DataFrame(columns=DATA_COLUMNS)

def init_dataframe_food():
    """Initialize or load the dataframe for fridge contents."""
    if 'df_food' not in st.session_state:
        if st.session_state.github.file_exists(DATA_FILE_FOOD):
            st.session_state.df_food = st.session_state.github.read_df(DATA_FILE_FOOD)
        else:
            st.session_state.df_food = pd.DataFrame(columns=DATA_COLUMNS_FOOD)

def show_login_page():
    col1, col2 = st.columns([7, 1])
    col2.image(small_image, use_column_width=False, clamp=True)
    
    st.title("Welcome to FreshAlert 😀, Let's start together with saving food") 
    st.title("Login")
    email = st.text_input("E-Mail", key="login_email")
    password = st.text_input("Passwort", type="password", key="login_password")
    if st.button("Login"):
        login_successful = False
        for index, row in st.session_state.df_login.iterrows():
            if row["E-Mail"] == email and row["Passwort"] == password:
                login_successful = True
                st.session_state.current_user_id = email  # Set current user ID
                break
        if login_successful:
            st.session_state.user_logged_in = True
            st.success("Erfolgreich eingeloggt!")
        else:
            st.error("Ungültige E-Mail oder Passwort.")
    if st.button("Registrieren", key="registration_button"):
        st.session_state.show_registration = True
    if st.session_state.get("show_registration", False):
        show_registration_page()

def show_registration_page():
    st.title("Registrieren")
           
    new_entry = {
        DATA_COLUMNS[0]: st.text_input(DATA_COLUMNS[0]), #Vorname
        DATA_COLUMNS[1]: st.text_input(DATA_COLUMNS[1]), #Nachname
        DATA_COLUMNS[2]: st.text_input(DATA_COLUMNS[2]), # E-Mail
        DATA_COLUMNS[3]: st.text_input(DATA_COLUMNS[3], type="password"), #Passwort
        DATA_COLUMNS[4]: st.text_input(DATA_COLUMNS[4], type="password"), #Passwort wiederholen
    }

    for key, value in new_entry.items():
        if value == "":
            st.error(f"Bitte ergänze das Feld '{key}'")
            return

    if st.button("Registrieren"):
        if new_entry["E-Mail"] in st.session_state.df_login["E-Mail"].values:
            st.error("Benutzer mit dieser E-Mail-Adresse ist bereits registriert.")
        else:
            if new_entry["Passwort"] == new_entry["Passwort wiederholen"]:
                new_entry_df = pd.DataFrame([new_entry])
                st.session_state.df_login = pd.concat([st.session_state.df_login, new_entry_df], ignore_index=True)
                save_data_to_database_login()
                st.success("Registrierung erfolgreich!")
                st.session_state.show_registration = False  # Reset status
            else:
                st.error("Die Passwörter stimmen nicht überein.")

def show_fresh_alert_page():
    col1, col2 = st.columns([7, 1])
    col2.image(small_image, use_column_width=False, clamp=True)
    st.title("FreshAlert")
    
    st.sidebar.image('images/18-04-_2024_11-16-47-Photoroom.png-Photoroom.png', use_column_width=True)

    # Create buttons for navigation
    navigation = st.sidebar.radio("Navigation", ["Startbildschirm", "Mein Kühlschrank", "Neues Lebensmittel hinzufügen", "Freunde einladen","Information", "Einstellungen", "Ausloggen"])

    # Check which page to display
    if navigation == "Startbildschirm":
        show_mainpage()
    elif navigation == "Mein Kühlschrank":
        show_my_fridge_page()
    elif navigation == "Neues Lebensmittel hinzufügen":
        add_food_to_fridge()
    elif navigation == "Freunde einladen":
        show_my_friends()
    elif navigation == "Information":
        show_informations()
    elif navigation == "Einstellungen":
        show_settings()
    elif navigation == "Ausloggen":
        logout()


def show_expired_food_on_mainpage():
    # Filtern aller Lebensmittel, die rot markiert sind (Ablaufdatum erreicht oder überschritten)
    expired_food = st.session_state.df_food[st.session_state.df_food['Tage_bis_Ablauf'] <= 1]

    if not expired_food.empty:
        st.markdown("---")
        st.subheader("Deine Lebensmittel, welche bald ablaufen!:")
        for index, row in expired_food.iterrows():
            st.error(f"**{row['Lebensmittel']}** (Ablaufdatum: {row['Ablaufdatum']}, Lagerort: {row['Lagerort']})")


def show_mainpage():
    st.subheader("Herzlich Willkommen bei FreshAlert. Deine App für deine Lebensmittel! ")            
    st.write("Füge links deine ersten Lebensmittel zu deinem Digitalen Kühlschrank hinzu. "
                 "Wir werden dich daran erinnern, es rechtzeitig zu benutzen und dir so helfen, keine Lebensmittel mehr zu verschwenden. "
                 "#StopFoodwaste ")
    st.write("HALLO IHR BEIDEN 🙈")
    #Zeigt die bald ablaufenden Lebensmittel an
    show_expired_food_on_mainpage()

def colorize_expiring_food(df):
    def colorize(val):
        if val <= 1:
            return 'color: red; font-weight: bold; font-size: 14px'
        elif  val == 2 or val ==3:
            return 'color: orange; font-weight: bold; font-size: 14px'
        else:
            return 'color: green; font-weight: bold; font-size: 14px'
    
    # Berechnung der Tage bis zum Ablaufdatum
    df['Tage_bis_Ablauf'] = (pd.to_datetime(df['Ablaufdatum']) - pd.Timestamp.now()).dt.days
    df['Tage_bis_Ablauf'] = df['Tage_bis_Ablauf'].apply(lambda x: 0 if x == -1 else x)  # Setze -1 auf 0
    
    # Einfärbung der Tabellenspalten und Formatierung der Zahlen
    df_styled = df.style.applymap(colorize, subset=['Tage_bis_Ablauf']).format({'Tage_bis_Ablauf': '{:.0f}'})
    
    return df_styled

def show_my_fridge_page():
    """Display the contents of the fridge."""
    st.title("Mein Kühlschrank")
    init_dataframe_food()  # Daten laden
    
    if not st.session_state.df_food.empty:
        # Filter entries based on current user ID (email)
        user_fridge = st.session_state.df_food[st.session_state.df_food['UserID'] == st.session_state.current_user_id]

        if not user_fridge.empty:
            # Sortiere das DataFrame nach den Tagen bis zum Ablaufdatum
            user_fridge = user_fridge.sort_values(by='Tage_bis_Ablauf', ascending=True)
            
            # Colorize the expiring food entries
            df_styled = colorize_expiring_food(user_fridge)
            
            # Display the formatted DataFrame
            st.write(df_styled)
            
            # Allow the user to delete a food entry
            index_to_delete = st.number_input("Index des zu löschenden Eintrags", min_value=0, max_value=len(user_fridge)-1, step=1)
            if st.button("Eintrag löschen", key="delete_entry_button"):
                st.session_state.df_food = st.session_state.df_food.drop(index=user_fridge.index[index_to_delete])
                save_data_to_database_food()  # Save the updated dataframe
                st.success("Eintrag erfolgreich gelöscht!")
        else:
            st.write("Der Kühlschrank ist leer für diesen Benutzer.")
    else:
        st.write("Der Kühlschrank ist leer.")

def add_food_to_fridge():
    st.title("Neues Lebensmittel hinzufügen")
           
    new_entry = {
        DATA_COLUMNS_FOOD[0]: st.session_state.current_user_id,  # UserID
        DATA_COLUMNS_FOOD[1]: st.text_input(DATA_COLUMNS_FOOD[1]), #Lebensmittel
        DATA_COLUMNS_FOOD[2]: st.selectbox("Kategorie", ["Bitte wählen","Gemüse", "Obst", "Milchprodukte", "Fleisch", "Fisch", "Eier", "Getränke", "Saucen", "Getreideprodukte", "Tiefkühlprodukte", "Gebäcke", "Sonstiges"]), #Kategorie
        DATA_COLUMNS_FOOD[3]: st.selectbox("Lagerort", ["Bitte wählen", "Schrank", "Kühlschrank", "Tiefkühler", "offen"]), # Location
        DATA_COLUMNS_FOOD[4]: st.selectbox("Standort", ["Bitte wählen", "Mein Kühlschrank", "geteilter Kühlschrank"]), #area
        DATA_COLUMNS_FOOD[5]: st.date_input("Ablaufdatum"), #Ablaufdatum
    }

    for key, value in new_entry.items():
        if value == "":
            st.error(f"Bitte ergänze das Feld '{key}'")
            return

    if st.button("Hinzufügen"):
        new_entry_df = pd.DataFrame([new_entry])
        st.session_state.df_food = pd.concat([st.session_state.df_food, new_entry_df], ignore_index=True)
        save_data_to_database_food()
        st.success("Lebensmittel erfolgreich hinzugefügt!")


def save_data_to_database_food():
    if 'github' in st.session_state:
        st.session_state.github.write_df(DATA_FILE_FOOD, st.session_state.df_food, "Updated food data")

def show_settings():
    st.title("Einstellungen")

def show_my_friends():
    st.title("Zeige deinen Freunden wie sie ihre Vorräte am besten organsieren können")
    st.write("Teile die App FreshAltert in dem du ihnen den Link unserer App schickst https://fresh-alert.streamlit.app/")
    st.write("Wir als Entwickler-Team würden uns riesig freuen")
    st.write("Liebe Grüsse von Mirco, Sarah und Sebastian, welche die App mit viel Liebe und noch mehr Schweiss und Tränen entwickelt haben")

def show_informations():
    st.title("Was ist Foodwaste?")
    st.image ("images/Foodwaste1.png")
    st.title("Tipps zur Reduzierung von Food Waste")
    st.header("Wo geschieht Foodwaste?")
    st.write("Die Gastronomie und die Haushalte verursachen zusammen 35% der Lebensmittelabfälle.")
    st.write("In den Haushalten entsteht Food Waste zum Beispiel, weil:")
    st.write("- wir mehr kaufen, als wir benötigen.")
    st.write("- wir größere Verpackungen kaufen, als wir brauchen.")
    st.write("- wir Lebensmittel im Kühlschrank vergessen.")
    st.write("- wir Lebensmittel nicht korrekt lagern und sich so die Haltbarkeit verringert.")
    st.write("- wir das Mindesthaltbarkeitsdatum mit dem Verbrauchsdatum verwechseln.")

    st.write("Die Folgen von Food Waste sind:")
    st.write("Es belastet nicht nur die Umwelt und das Klima, sondern kostet auch Geld und Ressourcen.")

    st.write("Quelle: https://www.foodwaste.ch/de/")

def logout():
    st.session_state.user_logged_in = False
    st.session_state.current_user_id = None

def save_data_to_database_login():
    if 'github' in st.session_state:
        st.session_state.github.write_df(DATA_FILE, st.session_state.df_login, "Updated login data")

def main():
    init_github()
    init_dataframe_login()
    init_dataframe_food()
    
    if st.session_state.user_logged_in:
        show_fresh_alert_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
