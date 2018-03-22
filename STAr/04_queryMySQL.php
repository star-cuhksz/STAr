<?php
$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "STAr";

$conn=new mysqli($servername,$username,$password,$dbname);
if($conn->connect_error){
    die("connect fail". $conn->connect_error);
}
echo "connect success!";
echo ini_set('max_execution_time','100');
$sql = "SELECT * FROM data";
while(1){
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        echo str_repeat("",1024);
        echo '<script>document.body.innerHTML="";</script>';
        while($row = $result->fetch_assoc())
        {
            echo "<br> id: ". $row["Id"]."bID:".$row["bID"]." rudder: ".$row["rudder"]." sail:".$row["sail"]." xPosition:".$row["xPosition"]." yPosition:".$row["yPosition"]."angle:".$row["angle"];
        }
        ob_flush();
        flush();
        sleep(1);
        echo '<script>windows.scrollTo(0,document.body.scrollHeight);</script>';
    } else {
        echo "0 result";
    }
}
$conn->close();
?>