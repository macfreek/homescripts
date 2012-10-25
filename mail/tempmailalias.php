#!/usr/bin/php -q
<?php

//$filename = "/etc/postfix/virtual";
//$filedir = "getenv("HOME");
//$filedir = dirname(__FILE__);
$file = "/etc/postfix/virtual";
$tempfile = "/tmp/virtual.temp";

$runafter = "/usr/sbin/postmap /etc/postfix/virtual";

// Take a day a bit in the future, as cron may run later during the day.
$today = time()+20*3600;
//$today = mktime(0,0,0,2,15,1981);
$day1ago   = mktime(0, 0, 0, date("m",$today), date("d",$today)-1, date("Y",$today));
$day2ago   = mktime(0, 0, 0, date("m",$today), date("d",$today)-2, date("Y",$today));
$day3ago   = mktime(0, 0, 0, date("m",$today), date("d",$today)-3, date("Y",$today));
$day4ago   = mktime(0, 0, 0, date("m",$today), date("d",$today)-4, date("Y",$today));
$day5ago   = mktime(0, 0, 0, date("m",$today), date("d",$today)-5, date("Y",$today));
$month1ago = mktime(0, 0, 0, date("m",$today)-1, 10,               date("Y",$today));
$month2ago = mktime(0, 0, 0, date("m",$today)-2, 10,               date("Y",$today));
$year1ago  = mktime(0, 0, 0, date("m",$today), date("d",$today),   date("Y",$today)-1);

$domain = "@macfreek.nl";
$tempmailaddresses = array(
    strftime("webmail%Y$domain",    $today),    // webmail2006
    strftime("webmail%Y$domain",    $month2ago),// retain previous year till march 1st
    strftime("freek%Y$domain",      $today),    // freek2006
    strftime("freek%Y$domain",      $year1ago), // freek2005
    strftime("freek%Y%m$domain",    $today),    // freek200609
    strftime("freek%Y%m$domain",    $month1ago),// freek200608
    strftime("freek%Y%m$domain",    $month2ago),// freek200607
    strftime("freek%Y%m%d$domain",  $today),    // freek20060916
    strftime("freek%Y%m%d$domain",  $day1ago),  // freek20060915
    strftime("freek%Y%m%d$domain",  $day2ago),  // freek20060914
    strftime("freek%Y%m%d$domain",  $day3ago),  // freek20060913
    strftime("freek%Y%m%d$domain",  $day4ago),  // freek20060912
    strftime("freek%Y%m%d$domain",  $day5ago),  // freek20060911
    );

$destination = "freek"; // recipient for temporary mail addresses
$paddingspaces = "                                "; // colon width

$startline = "# begin temporary mail addresses";
$endline   = "# end temporary mail addresses";
$start = null;
$end   = null;

if (!file_exists($file)):
    fprintf(STDERR, "file does not exist: $file\n");
    exit(74); // EX_IOERR in sysexits.h
endif;

$contents = file($file);
foreach ($contents as $lineno => $line):
    $line = trim($line);
    if ($line == $startline):
        if ($start != null) echo "warning: found two lines '$startline'\n";
        $start = $lineno;
        $end   = null;
    endif;
    if ($line == $endline):
        if ($end != null):
            echo "warning: found two lines '$endline'\n";
        else:
            $end = $lineno;
        endif;
    endif;
endforeach;
if ($start == null):
    echo "can not find line '$startline' in file $file\n";
    exit(65); // EX_DATAERR in sysexits.h
endif;
if ($end == null):
    echo "can not find line '$endline' after '$startline' in file $file\n"; 
    exit(65); // EX_DATAERR in sysexits.h
endif;

$tempmailaddresses = array_unique($tempmailaddresses);
foreach ($tempmailaddresses as $lineno => $line):
    $tempmailaddresses[$lineno] = $line.substr($paddingspaces,strlen($line)+1)." $destination\n";
endforeach;

array_splice($contents, $start+1, $end-$start-1, $tempmailaddresses);

file_put_contents($tempfile, implode("", $contents));
rename($tempfile, $file);

exec($runafter);

?>
