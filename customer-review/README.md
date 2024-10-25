# lab-iris

**Documentation**: [https://ai.veolia.tech/guidelines/guidelines/operationalization/lab-iris/intro/](https://ai.veolia.tech/guidelines/guidelines/operationalization/lab-iris/intro/) <br/>  
**Source code**: [https://gitlab.com/veolia.com/vesa/data-science/community/templates/lab-iris](https://gitlab.com/veolia.com/vesa/data-science/community/templates/lab-iris)

## Overview

The objective of this lab is to provide an example on how to leverage the
template [seed-fastapi-cloudrun](https://gitlab.com/veolia.com/vesa/data-science/community/templates/seed-fastapi-cloudrun)
. <br/>
In order to focus only on the api and deployment parts, we will remain very basic regarding the machine learning part
and simply work with a basic classifier on the classic [iris dataset](https://archive.ics.uci.edu/ml/datasets/iris).

## Objectives

1. train a model locally
2. deploy on cloud run an inference endpoint using this model trained locally
3. deploy on cloud run a training endpoint that will use the same training procedure used at step 1 (to be released
   soon)
4. deploy on cloud run a new inference endpoint using the model lastly trained in the cloud (to be released soon)

## Notes

The objective of this lab is to showcase some ways to speed up your operationalization flow.<br/>
It's only a proposition and you can customize it as much as you want.<br/>
In a continuous improvement dynamic, your feedbacks and contributions are
obviously very welcome ! 