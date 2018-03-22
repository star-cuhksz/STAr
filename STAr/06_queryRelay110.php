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

$sql = "SELECT relay1 FROM data WHERE Id=1";
$result = $conn->query($sql);
// $row=mysqli_fetch_array($result);
//echo $result;

$temp=10;
// suppose the value of temp matches the display angle directly
echo $temp;

$sql = "UPDATE data SET relay1=$temp WHERE Id=1";
$result = $conn->query($sql);
$conn->close();
?>