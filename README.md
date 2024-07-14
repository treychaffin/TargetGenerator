# Target Generator

Target generator I use to create paper target to assist with zeroing optics

## Example

![100yards_0-25moa.pn](./img/100yards_0-25moa.png)

## Dependencies

- [python](https://www.anaconda.com/download/success)
- [reportlab](https://pypi.org/project/reportlab/)
- [Flask](https://pypi.org/project/Flask/)

### Install dependencies with pip

    pip install -r requirements.txt

## Instructions for use

Run the `targetgenerator.py` file

    python targetgenerator.py

Open your web browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Docker Install

[https://hub.docker.com/r/treychaffin785/targetgenerator](https://hub.docker.com/r/treychaffin785/targetgenerator)

    docker container run -d -p 5000:5000 treychaffin785/targetgenerator:0.0.2