from elpris.view.cli import parse_arguments, vis_aktuel_pris_og_graf

if __name__ == "__main__":
    args = parse_arguments()
    vis_aktuel_pris_og_graf(
        region=args.region, 
        output_filename=args.output,
        show_plot=not args.no_show
    )
