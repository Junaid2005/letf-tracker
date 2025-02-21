
# LETF Tracker

This is a Python-based application that allows you to price Leveraged Exchange-Traded Funds (LETFs) against their underlying securities, when the LETF has stopped trading.

---
## Features
- **CLI**: Run the application directly from the command line.
- **GUI**: Run the application with an interactive UI via Streamlit.

### Core Features:
- **Search**: Price a LETF against its underlying security
- **Add**: Add a security pair to your dashboard.
- **Remove**: Remove a security pair from your dashboard.
- **Dashboard**: View all security pairs saved in your dashboard with relevant data.
- **Debug Mode**: Enable detailed logs for troubleshooting.
- **Email Results**: Automatically send the results to an email.
- **Trading 212 Account Integration**: Connect to Trading 212 account to get absolute changes in returns.
---

## Setup

Before running the app, make sure you have the following installed:

 **Python Version**  
 This app was developed with python version 3.12.6. Ensure you're using a compatible version.
 
 **Required libraries**:
You can install the required dependencies 
```bash
pip install -r requirements.txt
```
   
 **.env Setup (Recommended but not required)**:
To enable email functionality and Trading 212 integration, create a `.env` file in the `letf_tracker/` directory.

Example tructure for your .env file:
```
EMAIL_USER={your_email_here} 
EMAIL_PASS={your_password_here}
TRADING_212_KEY={your_key_here}
```
More details on setting up your email [here](https://support.google.com/accounts/answer/185833?hl=en)
More details on setting up your Trading 212 key [here](https://helpcentre.trading212.com/hc/en-us/articles/14584770928157-How-can-I-generate-an-API-key)

## Usage
For maximum functionality, please run from the `letf_tracker/` dir.
For optimum accuracy, RIC Codes are preferred over tickers and even ISINs.

#### Analysis

- **Search** for a LETF against its underlying security:
    ```bash
    python ./main/main.py -s {underlying_ticker} {letf_ticker}
    ```
    Example:
    ```bash
    python ./main/main.py -s COIN 3CON.L
    ```

- **Add** a security pair to your dashboard:
    ```bash
    python ./main/main.py -a {underlying_ticker} {letf_ticker}
    ```
    Example:
    ```bash
    python ./main/main.py -a COIN 3CON.L
    ```

- **Remove** a security pair from your dashboard:
    ```bash
    python ./main/main.py -r {underlying_ticker} {letf_ticker}
    ```
    Example:
    ```bash
    python ./main/main.py -r COIN 3CON.L
    ```

---

#### Dashboard

View and manage your dashboard of security pairs. You can also use the `-de` flag for debug mode or `-e` to email the results.

- **View Dashboard**:
    ```bash
    python ./main/main.py -d
    ```

- **View Dashboard with Absolute Change** (Trading 212 integration):
    ```bash
    python ./main/main.py -d -ac
    ```

---

#### GUI

Run the application with a graphical interface using **Streamlit**:

- **Start Streamlit UI**:
    ```bash
    python ./main/main.py -ui
    ```
