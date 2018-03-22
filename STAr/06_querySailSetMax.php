<?php
$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "STAr";

$conn = new mysqli($servername,$username,$password,$dbname);
if($conn->connect_error){
    die("connect fail". $conn->connect_error);
}
//echo ini_set('max_execution_time','100');

$sql = "SELECT sail FROM data WHERE Id=1";
$result = $conn->query($sql);
// $row = mysqli_fetch_array($result);
//echo $result;

$temp = 90;
// suppose the maximum angle is 90 degree
echo $temp;

$sql="UPDATE data SET sail=$temp WHERE Id=1";
$result = $conn->query($sql);
$conn->close();
?>