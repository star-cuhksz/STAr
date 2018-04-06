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
//Control left
$sql = "SELECT lmotor FROM data WHERE Id=1";
$result = $conn->query($sql);
$row=mysqli_fetch_array($result);
//echo $result;
if($row['lmotor']<110){
	$temp1=$row['lmotor']+1;
} else{
	$temp1=110;
}

//Control right
$sql = "SELECT rmotor FROM data WHERE Id=1";
$result = $conn->query($sql);
$row=mysqli_fetch_array($result);
//echo $result;
if($row['rmotor']<110){
	$temp2=$row['rmotor']+1;
} else{
	$temp2=110;
}

if($temp1<$temp2){
	$temp2=$temp1;
	//$temp1=87;
}
else{
	$temp1=$temp2;
}

echo "Left:",$temp1," Right:",$temp2;

$sql1 = "UPDATE data SET lmotor=$temp1 WHERE Id=1";
$result1 = $conn->query($sql1);

$sql2 = "UPDATE data SET rmotor=$temp2 WHERE Id=1";
$result2 = $conn->query($sql2);
$conn->close();
?>