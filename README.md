# Medicaid_2019_Qual_Measure
Visualization Project on the [2019 Medicaid Quality Measure Dataset](https://data.medicaid.gov/dataset/e36d89c0-f62e-56d5-bc7e-b0adf89262b8).

Please note that the graphs are rendered through nbviewer by clicking on the circle icon located in the upper right corner of the notebook. Or click on [View A](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/2019Medicaid.ipynb) or [View B](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/View%20B.ipynb).

## This visualization project has the following design goals: 
### Overview Across all Measure Types by State (View A)
CMS has simple visualizations on this dataset where viewers are able to select a certain state and Measure name. However this feature requires multiple visualizations for one arbitraty state given one specific Measure Name since a state will most likely be tracking several Measures in a given domain. Hence, a practical view that can compliment what is already available online is one that offers a 'snapshot' of each state by domain so that a viewer can easily spot measure names where that state is falling behind or doing well on, in a specific domain. Since there are only 5 different domains, our visualization will reduce the number of graphs that viewers will have to look through. </p> 

**Sample Visual:**
<img src="https://user-images.githubusercontent.com/29220349/131366354-5e957cb5-01fe-4218-8535-f431b9bb1adf.JPG" width="90%"></img> </p> 
Through this view, stakeholders can easily spot the Measures in a given domain where a given state is falling behind. 
 
### Overview Across all States by Measure  Type (View B) 
 </p>
Another valuable view is one that can show a 'snapshot' of all the states relative to a specific measure type where the states are arranged in ascending or descending order. This way, viewers can see the group of states that are in the top, median and bottom quartiles in terms of state rates for measures that these states have in common.
<img src="https://user-images.githubusercontent.com/29220349/134825488-439ed5fa-b1cb-4211-a211-2d17f262d912.JPG" width="90%"></img>

### Ambiguity with the Dataset </p> 
As illustrated below, some entries have indentical information except for the values in 'State Rate' and the corresponding 'Median', 'Top' and 'Bottom Values'. The original dataset did not include dates or other features that would make one entry more accurate than the other. From a general standpoint, we cannot discern which duplicate to keep and out of convinience, we just retained the first instance of a certain entry. 
<img src="https://user-images.githubusercontent.com/29220349/134824766-d20a9546-c3b4-4d96-bb69-914f7f6fd7c3.JPG" width="90%"></img> </p> 


