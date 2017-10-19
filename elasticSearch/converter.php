<?php
	require_once('arpabetToIPA.php');

	$t = new App();
	$raw = file_get_contents("cmudict-0.7b.txt");

	$lines = explode("\n", $raw);
	$myfile = fopen("cmudictIPA.txt", "w");
	foreach($lines as $line)
	{
		$pieces = explode("  ", $line);
		$token = strtolower($pieces[0]);
		$pron = $pieces[1];
		$nsyl = 0;
		for ($i = 0; $i < strlen($pron); $i++)
		{
		    if(is_numeric($pron[$i]))
		    {
		    	$nsyl++;
		    }
		}
		
		$ipa = $t->getIPA($pron);
		$outLine = $token."\t".$ipa."\t".$nsyl."\t".$pron."\n";
		fwrite($myfile, $outLine);
	}
	fclose($myfile);




?>