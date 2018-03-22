<?php
$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "STAr";

$conn=new mysqli($servername,$username,$password,$dbname);
if($conn->connect_error){
    die("connect fail". $conn->connect_error);
}
//echo ini_set('max_execution_time','100');

$sql = "SELECT lmotor FROM data WHERE Id=1";
$result = $conn->query($sql);
$row=mysqli_fetch_array($result);
//echo $result;
if($row['lmotor']>60){
	$temp=$row['lmotor']-1;
} else{
	$temp=60;
}
echo $temp;
$sql = "UPDATE data SET lmotor=$temp WHERE Id=1";
$result = $conn->query($sql);
$conn->close();
?>