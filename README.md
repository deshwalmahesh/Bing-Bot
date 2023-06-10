# Bing-Bot
Bing Chat automated with Selenium Web Driver to exchange messages. All the functions are in `helpers.py` in clss `BingGPT4` class. Use `chat` function to interact.`app.py` is just a `streamlit` wrapper around it to show how it's working. Read the `Docstring`.


Tested on `Ubuntu 20.04`. Needs to have `Edge`. You can use `sudo apt install microsoft-edge-dev`, `sudo apt install microsoft-edge-beta` or `sudo apt install microsoft-edge-stable` based on your OS. Alternatively [download it from here](https://www.microsoft.com/en-us/edge/download?form=MA13FJ)


You need a Webdriver which can be downloaded via `wget https://msedgedriver.azureedge.net/114.0.1823.18/edgedriver_linux64.zip`  based on your **EDGE VERSION**
> __Warning__ 
> MAKE SURE TO HAVE THE PATH OF THE `WebDriver` CORRECTLY AS IT IS USED TO LAUNCH THE DRIVER

# 
> __Note__:
> I implemented almost everything except the timing part. Right now you have to wait for a fixed time before the response is returned. 
If anyone can implement a dynamic version by checking regurlarly and returning the response as soon as it `finishes` (it can give half resilts too), please open a pull request.
```
