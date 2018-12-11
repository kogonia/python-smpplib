<?php

$html  = "<!doctype html>";
$html .= "
<html>
    <head>
        <title>SMS</title>
    </head>
    <body>";

$file  = file_get_contents('phone_list.txt');

$form = "
        <form name='sms_form' action='' method='POST'>
            <textarea name='sms_text' cols='40' rows='10' placeholder='Текст сообщения вводить сюда :)' autofocus></textarea>
            <textarea name='phone_list' cols='14' rows='10' placeholder='Номера здесь'>".$file."</textarea><br />
            <button type='submit' name='send' value='Submit'>Отправить</button>
        </form>";

$sms = $_POST['sms_text'];
$phones = $_POST['phone_list'];


if (isset($_POST['send'])){
    if (strlen($sms)>0 && strlen($phones)>0) {
        echo "Text: [ " . $sms . " ]<br />";
        exec("python3 my_tx.py '$phones' '$sms'", $result);
        var_dump($result);
    } else if (!strlen($sms)>0 && !strlen($phones)>0) {
        echo "Введите текст сообщения и номера телефонов!";
    } else if (strlen($sms)>0 && !strlen($phones)>0) {
        echo "Введите номера телефонов!";
    } else if (!strlen($sms)>0 && strlen($phones)>0) {
        echo "Введите текст сообщения!";
    }
}

$html .= $form;
$html .= "
    </body>
</html>";

echo $html;
?>
