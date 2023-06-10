# Bing-Bot
Bing Chat automated with Selenium Web Driver to exchange messages. Read the `Docstring` in case you have an issue using it

1. All the functions are `BingGPT4` class inside `helpers.py. 
2. Use `chat` function to interact
3. app.py` is just a `streamlit` wrapper around it to show how it's working

# 
+ Tested on `Ubuntu 20.04`. Needs to have `Edge`. You can use `sudo apt install microsoft-edge-dev`, `sudo apt install microsoft-edge-beta` or `sudo apt install microsoft-edge-stable` based on your OS. Alternatively [download it from here](https://www.microsoft.com/en-us/edge/download?form=MA13FJ)

# 
+ You need Edge Webdriver which can be downloaded [directly from this link](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) or via `wget https://msedgedriver.azureedge.net/114.0.1823.18/edgedriver_linux64.zip`. It is the file named `edge` here but you need to download based on **YOUR** OS and Edge Version.

# 
> __Warning__ 
> Make sure that the path of `WebDriver` is CORRECTLY passed to `BingGPT4` class as it is used to launch the driver

# 
> __Note__:
> I implemented almost everything except the response timing part. Right now you have to wait for a fixed time before the response is returned.
> If You wait too less, it'll give you half result or maybe `ElementNotFound` error and if you wait too long, it's a waste of time.
> So anyone having great knowledge of Selenium can implement a dynamic version by checking regurlarly and returning the response as soon as it finishes, please open a pull request.
```
