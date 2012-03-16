#!/usr/bin/php -qC
<?php

$srcdir = "/home/freek/Maildir/.Spam/cur";
$dstdir = "/home/freek/Maildir/.unfiltered/cur";

# Check if '/home/freek/pear' is in include_path
$extrapath = '/home/freek/pear';
$includepath = ini_get('include_path');
$includepath = explode(':', $includepath);
if (!in_array($extrapath, $includepath)) :
    # It's not. Add after '.' element, or at the start, if there is no '.' element.
    $pos = array_search('.', $includepath);
    if (is_int($pos)) { $pos++; } else { $pos = 0; }
    array_splice($includepath, $pos, 0, $extrapath);
    $includepath = implode(':', $includepath);
    ini_set('include_path', $includepath);
endif;

include_once 'Compat/Function/is_a.php';
include_once 'Console/Getopt.php';
include_once 'Mail/mimeDecode.php';

if (!empty($_ENV["PWD"])) chdir($_ENV["PWD"]);

list($options, $arguments) = Console_Getopt::getopt($argv, "sc:", array("silent","s","c="));

// correct for older (newer?) version of Getopt, which also included scriptname
if ($argv[0] == $arguments[0]) array_shift($arguments);
$options = flattenOptions($options);

if (count($arguments) == 1) :
    $dstdir = $arguments[0];
elseif (count($arguments) == 2) :
    $srcdir = $arguments[0];
    $dstdir = $arguments[1];
elseif (count($arguments) != 0) :
    usage();
endif;

$simulation = (isset($options['s']) or isset($options['simulation']));
if ($simulation)
    echo "Simulation mode\n";

echo "source directory:      $srcdir\n";
echo "destination directory: $dstdir\n";


$maxcount = (isset($options['c']) ? $options['c'] : 0);

function flattenOptions($array)
{
    $flatArray = array();
    foreach( $array as $subElement ) {
        if( is_array($subElement) )
            $flatArray[$subElement[0]] = (empty($subElement[1]) ? true : $subElement[1]);
    }
    return $flatArray;
}

function usage() {
    echo "extract-spame.php [-s|--simulation] sourcedir destdir\n";
    exit;
}

// echo "Start\n";

if (!is_dir($srcdir)) die("$srcdir is not a directory");
if (!is_dir($dstdir)) die("$dstdir is not a directory");

if ($handle = opendir($srcdir)) {
    // echo "Directory handle: $handle\n";
    // echo "Files:\n";
    /* This is the correct way to loop over the directory. */
    $count = 0;
    while (false !== ($file = readdir($handle))) {
        process_file($file);
        if (($count > $maxcount) and ($maxcount > 0)) break;
        $count++;
    }
    closedir($handle);
}

function process_file($file) {
    echo $file, " ... ";
    global $srcdir, $dstdir;
    global $simulation;
    if (!is_file($srcdir.'/'.$file)) {
        echo "skipped (not a regular file)\n";
        return false;
    }
    if (file_exists($dstdir.'/'.$file)) {
        if (unlink ($srcdir.'/'.$file)) {
            echo "deleted (destination file already exists)\n";
            return false;
        }
        echo "skipped (destination file already exists)\n";
        return false;
    }
    if (!is_readable($srcdir.'/'.$file)) {
        echo "skipped (source not readable)\n";
        return false;
    }
    if (!is_writable($dstdir.'/'.$file)) {
    // disabled because it gives false errors
//        echo "skipped (destination not writable)\n";
//        return false;
    }
    $fullmessage = implode('', file($srcdir.'/'.$file));
    $spammessage = get_spam_body($fullmessage);
    if ($spammessage === false) {
        echo "failed\n";
        return false;
    }
    if (!is_string($spammessage) or empty($spammessage)) {
        echo "(unexpected spammessage) failed\n";
        return false;
    }
    if ($simulation) {
        echo "(simulation only) skipped\n";
        return false;
    }

    # Write new spammessage to file
    if (!$handle = fopen($dstdir.'/'.$file, 'w')) {
        echo "(Cannot open file $dstdir.'/'.$file for writing) failed\n";
        return false;
    }
    if (fwrite($handle, $spammessage) === false) {
        echo "(Cannot write to file $dstdir.'/'.$file) failed\n";
        fclose($handle);
        return false;
    }
    if (!fclose($handle)) {
        echo "(Could not close file $dstdir.'/'.$file) failed?\n";
        fclose($handle);
        return false;
    }
    // done. delete original file.
    if (!unlink ($srcdir.'/'.$file)) {
        echo "(could not delete original file) done\n";
        return true;
    }
    echo "(original file deleted) done\n";
    return true;
}

function get_spam_body($fullmessage) {
    $mime = new Mail_mimeDecode($fullmessage);
    $message = $mime->decode(array('include_bodies' => true, 'decode_bodies' => false, 'decode_headers' => false));
    // First attempt: check for attachment with spam mail
    if (isset($message->parts) and is_array($message->parts)) {
        foreach($message->parts as $part) {
            // if ($part->headers['content-type'] == "message/rfc822; x-spam-type=original") {
            if (substr($part->headers['content-type'],0,14)  == "message/rfc822") {
                if (empty($part->body)) {
                    echo "(body of original mail empty; perhaps unmodified mimeDecode class?) \n";
                    return false;
                }
                return $part->body;
                break;
            }
        }
    }
    // Second attempt: check for "***SPAM*** " in subject
    if (!$found and isset($message->headers["subject"])) {
        $subject = $message->headers["subject"];
        if (strpos($subject, "***SPAM*** ") === 0) {
            // too complex to simplify header.
            $found = true;
            return $fullmessage;
        }
    }
    // nothing found
    return false;
}

// echo "Stop\n";

?>
