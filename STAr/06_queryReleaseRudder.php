<?php
$setServo=75;
$setStep=1;
$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "STAr";

$conn=new mysqli($servername,$username,$password,$dbname);
if($conn->connect_error){
    die("connect fail". $conn->connect_error);
}
//echo ini_set('max_execution_time','100');

$sql = "SELECT rudder FROM data WHERE Id=1";
$result = $conn->query($sql);
$row=mysqli_fetch_array($result);
//$tempRudder=$row['rudder'];
//echo $result;
/*
while ($tempRudder!=$setServo){
	if($tempRudder>$setServo){
		$temp=$tempRudder-$setStep;
	} else{
		$temp=$tempRudder+$setStep;
	}
	$tempRudder=$temp;
	echo $temp;
	$sql = "UPDATE data SET rudder=$temp WHERE Id=1";
	$result = $conn->query($sql);
	usleep(10000);
}
*/
	$temp=$setServo;
	echo $temp;
	$sql = "UPDATE data SET rudder=$temp WHERE Id=1";
	$result = $conn->query($sql);////
srrggecho $temp;
$conn->close();
?>