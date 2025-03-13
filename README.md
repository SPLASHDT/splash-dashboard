<p>
    <img src="assets/imgs/splash_logo.png">
    <img src="assets/imgs/splash_title.png" hspace="15" >
</p>

## DIGITAL APPROACHES TO PREDICT WAVE OVERTOPPING HAZARDS

### Advancing current understanding on wave-related coastal hazards

With sea level rise accelerating and weather extremes becoming increasingly stronger, tools to help climate adaptation of coastal communities are of paramount importance. SPLASH provides an overtopping tool that will act as forecast model directly helping coastal communities mitigate effects of this coastal hazard, and ultimately, guiding new climate adaptation strategies.

The model has been developed at the University of Plymouth Coastal Processes Research Group (CPRG) as part of the SPLASH project. The project was part of the Twinning Capability for the Natural Environment (TWINE) programme, designed to harness the potential of digital twinning technology to transform environmental science.

SPLASH digital twin is based on AI models trained using field measurements of wave overtopping. The model is updated once a day and uses Met Office wave and wind data as input, as well as predicted water level. This tool provides overtopping forecast 5 days ahead for Dawlish and Penzance, and allows the user to modify wind and wave input variables to test the sensitivity of wave overtopping.

# Documentation

More details about Splash project can be found in the following link: https://www.plymouth.ac.uk/research/coastal-processes/splash-project 

# Installation
## Run dashboard on any environment
1. Set a system environment variable temporarily using the following command in you terminal. Make sure you do not close terminal while running dashboard application. For example, to run dashboard locally, set SPLASH_ENV environment variable to _**local**_ value. For staging and production environments use _**staging**_ and _**production**_ values.

```bash
% export SPLASH_ENV="local"
```
2. To check system environment variable value, run the following command:

```bash
% echo $SPLASH_ENV
```

3. To run dashboard, run dashboard.py script using the following command:

```bash
% python3 dashboard.py
```

# Usage

You can access dashboard application locally by using the following link: http://127.0.0.1:8050/.
When accessing dashboard on other environments you must use a defined server domain. For example: https://splash.mydomain.net/