<?php

$dir = $_GET['dir'];
//echo $dir;

$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "STAr";

$conn=new mysqli($servername,$username,$password,$dbname);
if($conn->connect_error){
    die("connect fail". $conn->connect_error);
}
//echo ini_set('max_execution_time','100');


$temp=$dir;
//echo $temp;
$sql = "UPDATE data8802 SET D=$temp WHERE Id=1";
$result = $conn->query($sql);
$conn->close();
?>