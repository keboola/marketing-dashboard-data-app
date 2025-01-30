css_style = """
<style>
     .custom-column {
        margin: 20px;
    }

    .subheader {
        font-size: 24px;
        font-weight: bold;
        margin-top: 50px;
        margin-bottom:50px
    }

.subheader-2 {
        font-size: 21px;
        font-weight: bold;
        margin-top: 50px;
        margin-bottom:50px
    }


// HORNI METRIC //
    .div-container{
    display: flex;
    margin: 10px
    background-color: #F9F9F9;

}
.div-icon{
    border-radius: 50%;
    width: 6vw;
    height: 6vw; 
    flex-shrink: 0;
    background-color: #3CA0FF;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 1%;
}

.centered-text-h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
    text-align: left;
    line-height: 1.2;
}

.centered-text-p {
    margin: 5px 0 0;
    font-size: 24px;
    font-weight: bold;
    text-align: left;
    line-height: 0.001;
}

.icon-img{
    max-width: 50%;
    max-height: 50%;
    float: left;
}

.header{
    font-size: 15px;

}

.text{
    font-size: 26px;
    font-weight: bold;
    line-height: 2px;

}

.container {
  text-align: center;
  position: relative;
}

.container p {
  position: relative;
  z-index: 2;
}

.container img {
  position: relative;
  top: 20px; /* Adjust this value as needed */
  right: 5px
}


.centered-columns {
    display: flex;
    justify-content: center;
}

@media (max-width: 800px) {
    .div-container {
        flex-direction: column; 
        align-items: center;
        justify-content: center;
        
    }

    .div-icon{
    width: 60px;
    height: 60px; 
    }


    .icon-img{
    max-width: 40%;
    max-height: 40%;
    float: left;
    }
}
#add_margin_bottom{
    margin:20% 0;
}

@media (max-width: 638px) {
    .centered-text-h2 {

    text-align: center;

}

.centered-text-p {
    text-align: center;
   
}
}


</style>
"""
