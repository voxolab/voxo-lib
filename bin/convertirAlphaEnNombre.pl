#!/usr/bin/perl


if(scalar(@ARGV)!= 1) {
    print "USAGE : $0 nombreEnAlpha(exemple:quatre-vingt-cinq)\n";
    exit;
}


my %num_table;
my %num_alpha;

$alphaToConvert = $ARGV[0];

initNumberTab();

#Retourner table num_table;
foreach(sort keys %num_table){
	$nombre = $_;
	$alpha = $num_table{$nombre};
	$num_alpha{$alpha}=$nombre;
}

$alphaToConvert =~ s/-virgule-/,/g;

if($alphaToConvert =~ /([^,]+),(.+)/){
	$reste = $2;
	$avant = $1;
	$bef = convertAlphaToNumber($avant);
	$reste = $2;
	
	$ch = "";
	@infos = split(/-/, $reste);
	$end = 0;
	$i=0;
	$fin = "";
	for($i=0; $i<scalar(@infos)&&($end==0);$i++){
		$n = $infos[$i];
		$n =~ s/cents/cent/g;
                $n =~ s/milles/mille/g;
                $n =~ s/millions/million/g;
                $n =~ s/milliards/milliard/g;
		if( ($n eq "cent") || ($n eq "mille") || ($n eq "million") || ($n eq "milliard")){
			$end = 1;
			$fin = $n;
		}else{
			$ch .= $n."-";
		}
	}
	chop($ch) if($ch ne "");
	$reste = convertAlphaToNumber($ch)." ".$fin;
	print $bef.",".$reste."\n";
}else{
	print convertAlphaToNumber($alphaToConvert)."\n";
}

sub convertAlphaToNumber{
	my $alphaToConvert = $_[0];
	my $ajoutIeme=0;

	if($alphaToConvert =~ /(.*)ième/){
		$chi=$1;
		$alphaToConvert =~ s/neuv/neuf/g;
		$alphaToConvert =~ s/cinquième/cinqième/g;
		if($alphaToConvert =~ /(.*)ième/){
			$chi = $1;
		}
		@temp = split(/-/, $chi);
		$chif=$temp[scalar(@temp)-1];
		#quatorz ieme cinquant ieme ...
		if( ($chif eq "mill") || ($chif eq "million") || ($chif eq "milliard")) {
			if($chif eq "mill"){
				$alphaToConvert = $chi."e";
			}	
		}elsif(exists($num_alpha{$chif."e"})){
			$alphaToConvert = $chi."e";
		}else{
			$alphaToConvert = $chi;
			@temp = split(/-/, $chi);
			$chif=$temp[scalar(@temp)-1];
			if(!exists($num_alpha{$chif})){
				return "ERROR ! ($chif)\n";
			}	
		}
		$ajoutIeme = 1;
	}

	$milliards = makeMilliards($alphaToConvert);
@infos = split(/\#/, $milliards);

$milliards = $infos[0];
$reste = $infos[1];

$milliards_million = makeMillions($milliards);
@infos = split(/\#/, $milliards_million);
$milliards_million=$infos[0];
$reste_milliards_million = $infos[1];


$milliards_milliers=makeMilliers($milliards_million);
@infos = split(/\#/, $milliards_milliers);
$milliards_milliers = makeCentaineEtDizaine($infos[0]);
$milliards_milliers_centdiz = makeCentaineEtDizaine($infos[1]);


$milliards_milliers_reste = makeMilliers($reste_milliards_million);
@infos = split(/\#/, $milliards_milliers_reste);
$milliards_milliers_reste = makeCentaineEtDizaine($infos[0]);
$milliards_milliers_reste_centdiz = makeCentaineEtDizaine($infos[1]);


$monNombre = ($milliards_milliers*1000+$milliards_milliers_centdiz)*1000000+$milliards_milliers_reste*1000+$milliards_milliers_reste_centdiz;
$monNombre = $monNombre*1000000000;

$millions = makeMillions($reste);
@infos = split(/#/, $millions);

$millions = $infos[0];
$reste = $infos[1];


$million_millier = makeMilliers($millions);
@infos = split(/#/, $million_millier);
$million_millier = makeCentaineEtDizaine($infos[0]);
$millions_millier_reste = makeCentaineEtDizaine($infos[1]);
$monNombre = $monNombre + ($million_millier*1000+$millions_millier_reste)*1000000;

$milliers = makeMilliers($reste);
@infos = split(/#/, $milliers);

$milliers = makeCentaineEtDizaine($infos[0]);
$reste = makeCentaineEtDizaine($infos[1]);


$monNombre = $monNombre+$milliers*1000+$reste;

	if($ajoutIeme == 1){
		return $monNombre."ème";
	}

	if($alphaToConvert =~ /^z[^-]+ro-/) {
        return '0' . $monNombre;
    } else {
        return $monNombre;
    }

}


sub makeCentaineEtDizaine{
        my $chaine = $_[0];
        #Dizaines
        $chaine =~ s/\-et\-/\-/g;
        my @nums = split(/\-/, $chaine);
        my $nombre = 0;
        for($i=scalar(@nums)-1; $i>=0; $i--){
                my $n = $nums[$i];
                $n =~ s/cents/cent/g;
                $n =~ s/milles/mille/g;
                $n =~ s/millions/million/g;
                $n =~ s/milliards/milliard/g;
		if( ($n ne "cent") && ($n ne "mille") && ($n ne "million") && ($n ne "milliard") && ($n ne "vingt")){
                                $nombre += $num_alpha{$n};
                }else{
                        if($n eq "cent"){
                                #cherche le chiffre precedent
                                $cent = 1;
                                if( ($i-1)>=0){
                                        $chPrec = $nums[$i-1];
                                        die "Wrong number of centaine $chPrec...\n" if(!exists($num_alpha{$chPrec}));
                                        $i--;
                                        $cent = $num_alpha{$chPrec};
                                }
                                $nombre += ($cent*100);
                        }elsif($n eq "vingt"){
				#cherche le chiffre precedent
				$vingt = 20;
				if( ($i-1)>=0){
                                        $chPrec = $nums[$i-1];
					if($chPrec eq "quatre"){
						$vingt = $vingt*4;
						$i--;
					}
				}
				$nombre += $vingt;	
			}
                }
        }
        return $nombre;
}

sub makeMilliers{
	my $chaine = $_[0];
        $chaine =~ s/\-et\-/\-/g;
        my @nums = split(/\-/, $chaine);

        my $mille = "";
	my $reste = "";

                #Cherche tout ce qui est à multiplier par milliard
                my $nombre = 0;
                my $fin = 0;
        $fin = 1 if($chaine !~ /mille/);
	for($i=0; $i<scalar(@nums); $i++){
                        my $n = $nums[$i];
                        $n =~ s/cents/cent/g;
                        $n =~ s/milles/mille/g;
                        $n =~ s/millions/million/g;
                        $n =~ s/milliards/milliard/g;
                        if($n eq "mille"){
                                $fin = 1;
                        }
			if($fin == 0){
				$mille .= $n."-";
			}else{
				if($n ne "mille"){
					$reste .= $n."-";
				}
			}
                }
                if($mille ne ""){
                        chop($mille);
               	} 
        
		if($reste ne ""){
			chop($reste);
		}

	if($chaine =~ /mille/ && $mille eq ""){
		$mille = "un";
	}
	return $mille."#".$reste;

}

sub makeMillions{
	my $chaine = $_[0];
        $chaine =~ s/\-et\-/\-/g;
        my @nums = split(/\-/, $chaine);

        my $million = "";
        my $reste = "";
        #Cherche tout ce qui est à multiplier par milliard
        my $nombre = 0;
        my $fin = 0;
        $fin = 1 if($chaine !~ /million/);
	for($i=0; $i<scalar(@nums); $i++){
                my $n = $nums[$i];
                $n =~ s/cents/cent/g;
                $n =~ s/milles/mille/g;
                $n =~ s/millions/million/g;
                $n =~ s/milliards/milliard/g;
                if($n eq "million"){
                        $fin = 1;
                }
		if($fin == 0){
                        $million .= $n."-";
                }else{
			if($n ne "million"){
				$reste .= $n."-";
			}
		}
        }
        if($million ne ""){
		chop($million);
	}
        if($reste ne ""){
		chop($reste);
	} 
	return $million."#".$reste;
}

sub makeMilliards{
	my $chaine = $_[0];
	$chaine =~ s/\-et\-/\-/g;
        my @nums = split(/\-/, $chaine);

	my $milliard = "";
	my $reste = "";
	
	#Cherche tout ce qui est à multiplier par milliard
	my $nombre = 0;
	my $fin = 0;
	$fin = 1 if($chaine !~ /milliard/);
	for($i=0; $i<scalar(@nums); $i++){
		my $n = $nums[$i];
		$n =~ s/cents/cent/g;
               	$n =~ s/milles/mille/g;
               	$n =~ s/millions/million/g;
               	$n =~ s/milliards/milliard/g;
		if($n eq "milliard"){
			$fin = 1;
		}
		if($fin == 0){
			$milliard .= $n."-";
		}else{
			if($n ne "milliard"){
				$reste .= $n."-";
			}
		}
	}
	if($milliard ne ""){
		chop($milliard);
	}	

	if($reste ne ""){

		chop($reste);
	}

	return $milliard."#".$reste;
}

sub initNumberTab{
    %num_table=("0"=>"zéro","1"=>"un",
                "2"=>"deux",
                "3"=>"trois",
                "4"=>"quatre",
                "5"=>"cinq",
                "6"=>"six",
                "7"=>"sept",
                "8"=>"huit",
                "9"=>"neuf",
                "10"=>"dix",
                "11"=>"onze",
                "12"=>"douze",
                "13"=>"treize",
                "14"=>"quatorze",
                "15"=>"quinze",
                "16"=>"seize",
                "20"=>"vingt",
                "21"=>"vingt-et-un",
                "30"=>"trente",
                "31"=>"trente-et-un",
                "40"=>"quarante",
                "41"=>"quarante-et-un",
                "50"=>"cinquante",
                "51"=>"cinquante-et-un",
                "60"=>"soixante",
                "70"=>"soixante-dix",
                "71"=>"soixante-et-onze",
                "72"=>"soixante-douze",
                "73"=>"soixante-treize",
                "74"=>"soixante-quatorze",
                "75"=>"soixante-quinze",
                "76"=>"soixante-seize",
                "77"=>"soixante-dix-sept",
                "78"=>"soixante-dix-huit",
                "79"=>"soixante-dix-neuf",
                "80"=>"quatre-vingt",
                "90"=>"quatre-vingt-dix",
                "91"=>"quatre-vingt-onze",
                "92"=>"quatre-vingt-douze",
                "93"=>"quatre-vingt-treize",
                "94"=>"quatre-vingt-quatorze",
                "95"=>"quatre-vingt-quinze",
                "96"=>"quatre-vingt-seize",
                "97"=>"quatre-vingt-dix-sept",
                "98"=>"quatre-vingt-dix-huit",
                "99"=>"quatre-vingt-dix-neuf");
    
}

sub TransDizaine{
    my $i=0;
    my $number = $_[$i++];
    if(exists($num_table{$number})){
        return $num_table{$number};
    }else{
        $dizaine = int($number/10)*10;
        $unite = $number-$dizaine;
        $ch1 = $num_table{$dizaine};
        $ch2 = $num_table{$unite};
        return "$ch1-$ch2";
    }
}

sub TransCentaine{
    my $i=0;
    my $number = $_[$i++];
    #my $centaine = substr($number,0,1);
	my $centaine = int($number/100);
    my $alpha_centaine = "";
    if($centaine > 1){
        $alpha_centaine = $num_table{$centaine} . "-";
    	$alpha_centaine = $alpha_centaine . "cent";
    }elsif($centaine == 1){
    	$alpha_centaine = $alpha_centaine . "cent";	
    }
    my $dizaine = $number - $centaine*100;
    my $alpha_dizaine = "";
    if($dizaine > 0){
    	if($centaine > 0){
    		$alpha_dizaine = "-";	
    	}
        $alpha_dizaine .= TransDizaine($dizaine);
    }
    return $alpha_centaine . $alpha_dizaine;
}

sub TransMillier{
    my $i=0;
    my $number = $_[$i++];
    my $millier = int($number/1000);
    my $centaine = $number - $millier*1000;
    my $alpha_centaine = "";
    my $alpha_millier="";
    my $n = length($millier);
    if($n<=2){
        if($millier > 1){
            $alpha_millier = TransDizaine($millier). "-mille";
        }else{
            $alpha_millier = "mille";
        }
    }elsif($n<=3){
        $alpha_millier = TransCentaine($millier). "-mille";
    }
    if($centaine != 0){
        $alpha_centaine = "-".TransCentaine($centaine);
    }
    
    return $alpha_millier . $alpha_centaine;
}

sub TransMillion{
    my $i=0;
    my $number = $_[$i++];
    my $million = int($number/1000000);
    my $millier = $number - $million*1000000;
    my $alpha_millier = "";
    my $alpha_million="";
    my $n = length($million);
    
    $alpha_million = convertNumberToAlpha($million). "-million";
    if($millier > 0){
        $alpha_millier = "-".convertNumberToAlpha($millier);
    }
    
    return $alpha_million . $alpha_millier;
}

sub TransMilliard{
    my $i=0;
    my $number = $_[$i++];
    my $milliard = int($number/1000000000);
    my $million = $number - $milliard*1000000000;
    my $alpha_million = "";
    my $alpha_milliard = "";
    my $n = length($milliard);
    
    $alpha_milliard = convertNumberToAlpha($milliard) . "-milliard";
    if($million > 0){
        $alpha_million = "-".convertNumberToAlpha($million);
    }
    return $alpha_milliard.$alpha_million;
}


sub convertNumberToAlpha{
    my $i=0;
    my $number = $_[$i++];
    my $n = length($number);
    if($n != 0){
        if($n <= 2){
            return TransDizaine($number);
        }elsif($n <= 3){
            return TransCentaine($number);
        }elsif($n <= 6){
            return TransMillier($number);
        }elsif($n <= 9){
            return TransMillion($number);
        }else{
            return TransMilliard($number);
        }
    }
    
}






