#!/usr/bin/perl


if(scalar(@ARGV)!= 1) {
    print "USAGE : $0 nombre\n";
    exit;
}


my %num_table;
$nombre = $ARGV[0];


if(isANumber($nombre)){
	initNumberTab();
	$alpha = convertNumberToAlpha($nombre);
	#$alpha =~ s/\-/ /g;
	print $alpha."\n";
}else{
	print "BadNumber\n";
}

sub isANumber{
    my $i=0;
    my $chaine = $_[$i++]. " ";
    if($chaine =~ /^[0-9]+[ ]/){
        return 1;
    }else{
        return 0;
    }
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
                "61"=>"soixante-et-un",
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
                "99"=>"quatre-vingt-dix-neuf",
                ""=>"");
    
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






